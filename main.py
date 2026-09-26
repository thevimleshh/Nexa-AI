
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware

import os
import requests
import mysql.connector
import bcrypt

from ai_model import get_ai_response
from context_manager import manage_context
from vision import get_vision_response
from memory import (
    save_memory,
    should_save_memory,
    get_memories
)


# =========================
# LOAD ENVIRONMENT
# =========================

load_dotenv()


# =========================
# FASTAPI APP
# =========================

app = FastAPI()


# =========================
# SESSION
# =========================

SESSION_SECRET = os.getenv(
    "SESSION_SECRET",
    "nexa-ai-super-secret-key"
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET
)


# =========================
# STATIC FILES
# =========================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =========================
# TEMPLATES
# =========================

templates = Jinja2Templates(
    directory="templates"
)


# =========================
# DATABASE
# =========================

def get_db_connection():

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )


# =========================
# REQUEST MODELS
# =========================

class ChatRequest(BaseModel):

    message: str
    conversation_id: int | None = None


class SignupRequest(BaseModel):

    name: str
    email: str
    password: str


class LoginRequest(BaseModel):

    email: str
    password: str


class ChangePasswordRequest(BaseModel):

    current_password: str
    new_password: str
    confirm_password: str


# =========================
# HOME
# =========================

@app.get("/")
async def home(request: Request):

    user_id = request.session.get("user_id")

    if not user_id:

        return templates.TemplateResponse(
            request=request,
            name="login.html"
        )

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# =========================
# LOGIN PAGE
# =========================

@app.get("/login")
async def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


# =========================
# SIGNUP PAGE
# =========================

@app.get("/signup")
async def signup_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="signup.html"
    )


# =========================
# SIGNUP API
# =========================

@app.post("/api/signup")
async def signup(request: SignupRequest):

    name = request.name.strip()
    email = request.email.strip().lower()
    password = request.password

    if not name:

        return {
            "success": False,
            "error": "Name is required."
        }

    if not email:

        return {
            "success": False,
            "error": "Email is required."
        }

    if len(password) < 8:

        return {
            "success": False,
            "error": "Password must be at least 8 characters."
        }

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            return {
                "success": False,
                "error": "An account with this email already exists."
            }

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (
                name,
                email,
                hashed_password
            )
        )

        db.commit()

        return {
            "success": True
        }

    except Exception as error:

        print("Signup error:", error)

        return {
            "success": False,
            "error": "Unable to create account."
        }

    finally:

        cursor.close()
        db.close()


# =========================
# LOGIN API
# =========================

@app.post("/api/login")
async def login(
    request: Request,
    login_data: LoginRequest
):

    email = login_data.email.strip().lower()
    password = login_data.password

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT id, name, email, password
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:

            return {
                "success": False,
                "error": "Invalid email or password."
            }

        password_correct = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password"].encode("utf-8")
        )

        if not password_correct:

            return {
                "success": False,
                "error": "Invalid email or password."
            }

        request.session["user_id"] = user["id"]

        return {
            "success": True
        }

    except Exception as error:

        print("Login error:", error)

        return {
            "success": False,
            "error": "Unable to login."
        }

    finally:

        cursor.close()
        db.close()


# =========================
# CURRENT USER
# =========================

@app.get("/api/me")
async def get_current_user(
    request: Request
):

    user_id = request.session.get("user_id")

    if not user_id:

        return {
            "logged_in": False
        }

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT id, name, email
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:

            request.session.clear()

            return {
                "logged_in": False
            }

        return {
            "logged_in": True,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        }

    finally:

        cursor.close()
        db.close()


# =========================
# CHAT API
# =========================

@app.post("/api/chat")
async def chat(
    http_request: Request,
    request: ChatRequest
):

    user_id = http_request.session.get("user_id")

    if not user_id:

        return {
            "error": "Please login first."
        }

    if not request.message.strip():

        return {
            "error": "Message cannot be empty."
        }

    if len(request.message) > 5000:

        return {
            "error": (
                "Message is too long. "
                "Please keep it under 5000 characters."
            )
        }

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        # =========================
        # CREATE / USE CONVERSATION
        # =========================

        conversation_id = request.conversation_id

        if conversation_id:

            cursor.execute(
                """
                SELECT id
                FROM conversations
                WHERE id = %s
                AND user_id = %s
                """,
                (
                    conversation_id,
                    user_id
                )
            )

            conversation = cursor.fetchone()

            if not conversation:

                return {
                    "error": "Conversation not found."
                }

        else:

            title = request.message.strip()

            if len(title) > 255:

                title = title[:255]

            cursor.execute(
                """
                INSERT INTO conversations
                (title, user_id)
                VALUES (%s, %s)
                """,
                (
                    title,
                    user_id
                )
            )

            db.commit()

            conversation_id = cursor.lastrowid

        # =========================
        # SAVE USER MESSAGE
        # =========================

        cursor.execute(
            """
            INSERT INTO messages
            (conversation_id, role, content)
            VALUES (%s, %s, %s)
            """,
            (
                conversation_id,
                "user",
                request.message
            )
        )

        db.commit()

        # =========================
        # SAVE MEMORY
        # =========================

        if should_save_memory(request.message):

            save_memory(
                user_id,
                request.message
            )

        # =========================
        # GET CHAT HISTORY
        # =========================

        cursor.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = %s
            ORDER BY id ASC
            """,
            (conversation_id,)
        )

        previous_messages = cursor.fetchall()

        # =========================
        # MANAGE CONTEXT
        # =========================

        previous_messages = manage_context(
            previous_messages,
            max_tokens=4000
        )

        # =========================
        # GET USER MEMORIES
        # =========================

        memories = get_memories(user_id)

        memory_text = ""

        if memories:

            memory_text = "\n\n".join(
                memory["memory"]
                for memory in memories
            )

       

        # =========================
        # GET AI RESPONSE
        # =========================

        try:

            ai_reply = get_ai_response(
                previous_messages,
                temperature=0.7,
                memory_text=memory_text
            )

        except requests.exceptions.Timeout:

            return {
                "reply": (
                    "The AI service took too long "
                    "to respond. Please try again."
                ),
                "conversation_id": conversation_id
            }

        except requests.exceptions.RequestException as error:

            print(
                "OpenRouter request error:",
                error
            )

            return {
                "reply": (
                    "Unable to connect to the AI "
                    "service. Please try again."
                ),
                "conversation_id": conversation_id
            }

        except Exception as error:

            print(
                "AI error:",
                error
            )

            return {
                "reply": (
                    "Something went wrong while "
                    "generating the AI response."
                ),
                "conversation_id": conversation_id
            }

        # =========================
        # SAVE AI RESPONSE
        # =========================

        cursor.execute(
            """
            INSERT INTO messages
            (conversation_id, role, content)
            VALUES (%s, %s, %s)
            """,
            (
                conversation_id,
                "assistant",
                ai_reply
            )
        )

        db.commit()

        return {
            "reply": ai_reply,
            "conversation_id": conversation_id
        }

    except Exception as error:

        print(
            "Chat error:",
            error
        )

        return {
            "error": "Something went wrong."
        }

    finally:

        cursor.close()
        db.close()


# =========================
# GET CHAT HISTORY
# =========================

@app.get("/api/conversations")
async def get_conversations(
    request: Request
):

    user_id = request.session.get("user_id")

    if not user_id:

        return {
            "error": "Please login first."
        }

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT id, title, created_at
            FROM conversations
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,)
        )

        conversations = cursor.fetchall()

        return {
            "conversations": conversations
        }

    finally:

        cursor.close()
        db.close()


# =========================
# OPEN CONVERSATION
# =========================

@app.get(
    "/api/conversations/{conversation_id}"
)
async def open_conversation(
    request: Request,
    conversation_id: int
):

    user_id = request.session.get("user_id")

    if not user_id:

        return {
            "error": "Please login first."
        }

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT id
            FROM conversations
            WHERE id = %s
            AND user_id = %s
            """,
            (
                conversation_id,
                user_id
            )
        )

        conversation = cursor.fetchone()

        if not conversation:

            return {
                "error": "Conversation not found."
            }

        cursor.execute(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY id ASC
            """,
            (conversation_id,)
        )

        messages = cursor.fetchall()

        return {
            "conversation_id": conversation_id,
            "messages": messages
        }

    finally:

        cursor.close()
        db.close()


# =========================
# DELETE CONVERSATION
# =========================

@app.delete(
    "/api/conversations/{conversation_id}"
)
async def delete_conversation(
    request: Request,
    conversation_id: int
):

    user_id = request.session.get("user_id")

    if not user_id:

        return {
            "error": "Please login first."
        }

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM conversations
            WHERE id = %s
            AND user_id = %s
            """,
            (
                conversation_id,
                user_id
            )
        )

        db.commit()

        return {
            "success": True
        }

    finally:

        cursor.close()
        db.close()


# =========================
# LOGOUT
# =========================

@app.post("/api/logout")
async def logout(
    request: Request
):

    request.session.clear()

    return {
        "success": True
    }


# =========================
# CHANGE PASSWORD
# =========================

@app.post("/api/change-password")
async def change_password(
    request: Request,
    password_data: ChangePasswordRequest
):

    user_id = request.session.get("user_id")

    if not user_id:

        return {
            "success": False,
            "error": "Please login first."
        }

    current_password = (
        password_data.current_password
    )

    new_password = (
        password_data.new_password
    )

    confirm_password = (
        password_data.confirm_password
    )

    if not current_password:

        return {
            "success": False,
            "error": "Current password is required."
        }

    if not new_password:

        return {
            "success": False,
            "error": "New password is required."
        }

    if len(new_password) < 8:

        return {
            "success": False,
            "error": (
                "New password must be at least "
                "8 characters."
            )
        }

    if new_password != confirm_password:

        return {
            "success": False,
            "error": "New passwords do not match."
        }

    if current_password == new_password:

        return {
            "success": False,
            "error": (
                "New password must be different "
                "from current password."
            )
        }

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT password
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:

            return {
                "success": False,
                "error": "User not found."
            }

        password_correct = bcrypt.checkpw(
            current_password.encode("utf-8"),
            user["password"].encode("utf-8")
        )

        if not password_correct:

            return {
                "success": False,
                "error": "Current password is incorrect."
            }

        hashed_password = bcrypt.hashpw(
            new_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        cursor.execute(
            """
            UPDATE users
            SET password = %s
            WHERE id = %s
            """,
            (
                hashed_password,
                user_id
            )
        )

        db.commit()

        return {
            "success": True
        }

    except Exception as error:

        print(
            "Change password error:",
            error
        )

        return {
            "success": False,
            "error": "Unable to change password."
        }

    finally:

        cursor.close()
        db.close()


# =========================
# VISION API
# =========================

@app.post("/api/vision")
async def vision(
    request: Request
):

    # =========================
    # CHECK LOGIN
    # =========================

    user_id = request.session.get("user_id")

    if not user_id:

        return {
            "error": "Please login first."
        }


    # =========================
    # GET FORM DATA
    # =========================

    form = await request.form()

    image = form.get("image")
    question = form.get("question", "")


    # =========================
    # CHECK IMAGE
    # =========================

    if not image:

        return {
            "error": "Please upload an image."
        }


    # =========================
    # CHECK QUESTION
    # =========================

    question = question.strip()

    if not question:

        question = (
            "Describe this image and explain "
            "what you can see."
        )


    # =========================
    # CHECK IMAGE TYPE
    # =========================

    if not image.content_type:

        return {
            "error": "Invalid image file."
        }


    if not image.content_type.startswith("image/"):

        return {
            "error": "Please upload a valid image."
        }


    # =========================
    # READ IMAGE
    # =========================

    try:

        image_bytes = await image.read()

    except Exception as error:

        print(
            "Image read error:",
            error
        )

        return {
            "error": "Unable to read the image."
        }


    # =========================
    # IMAGE SIZE CHECK
    # =========================

    max_image_size = 10 * 1024 * 1024

    if len(image_bytes) > max_image_size:

        return {
            "error": (
                "Image is too large. "
                "Maximum size is 10 MB."
            )
        }


    # =========================
    # SEND TO VISION AI
    # =========================

    try:

        ai_reply = get_vision_response(
            image_bytes=image_bytes,
            content_type=image.content_type,
            question=question
        )


    except requests.exceptions.HTTPError as error:

        print(
            "Vision API HTTP error:",
            error
        )


        # =========================
        # GET STATUS CODE
        # =========================

        status_code = (
            error.response.status_code
            if error.response
            else 500
        )


        # =========================
        # RATE LIMIT
        # =========================

        if status_code == 429:

            return {
                "error": (
                    "Vision AI is temporarily "
                    "rate-limited. Please try again "
                    "in a few seconds."
                )
            }


        # =========================
        # OTHER HTTP ERROR
        # =========================

        return {
            "error": (
                "Vision AI returned an error "
                f"(HTTP {status_code})."
            )
        }


    except requests.exceptions.Timeout:

        return {
            "error": (
                "Vision AI took too long to respond. "
                "Please try again."
            )
        }


    except requests.exceptions.RequestException as error:

        print(
            "Vision API request error:",
            error
        )

        return {
            "error": (
                "Unable to connect to Vision AI. "
                "Please try again."
            )
        }


    except Exception as error:

        print(
            "Vision AI error:",
            error
        )

        return {
            "error": (
                "Something went wrong while "
                "analyzing the image."
            )
        }


    # =========================
    # RETURN AI RESPONSE
    # =========================

    return {
        "success": True,
        "reply": ai_reply
    }

