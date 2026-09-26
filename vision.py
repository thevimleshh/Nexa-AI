import os
import base64
import requests

from dotenv import load_dotenv


# =========================
# LOAD ENVIRONMENT
# =========================

load_dotenv()


# =========================
# OPENROUTER
# =========================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)


# =========================
# VISION MODEL
# =========================

VISION_MODEL = "openrouter/free"


# =========================
# IMAGE TO BASE64
# =========================

def image_to_base64(
    image_bytes,
    content_type
):

    encoded_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    return (
        f"data:{content_type};base64,"
        f"{encoded_image}"
    )


# =========================
# ASK VISION AI
# =========================

def get_vision_response(
    image_bytes,
    content_type,
    question
):

    if not OPENROUTER_API_KEY:

        raise Exception(
            "OPENROUTER_API_KEY is missing."
        )


    # =========================
    # CHECK IMAGE
    # =========================

    if not image_bytes:

        raise Exception(
            "Image data is empty."
        )


    print(
        "VISION IMAGE SIZE:",
        len(image_bytes),
        "bytes"
    )

    print(
        "VISION IMAGE TYPE:",
        content_type
    )


    # =========================
    # CONVERT IMAGE
    # =========================

    image_data = image_to_base64(
        image_bytes,
        content_type
    )


    print(
        "BASE64 IMAGE CREATED:",
        len(image_data),
        "characters"
    )


    # =========================
    # HEADERS
    # =========================

    headers = {

        "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
            "application/json",

        "HTTP-Referer":
            "http://127.0.0.1:8000",

        "X-Title":
            "Nexa AI"

    }


    # =========================
    # REQUEST DATA
    # =========================

    data = {

        "model": VISION_MODEL,

        "temperature": 0.7,

        "messages": [

            {

                "role": "user",

                "content": [

                    {

                        "type": "text",

                        "text": question

                    },

                    {

                        "type": "image_url",

                        "image_url": {

                            "url": image_data

                        }

                    }

                ]

            }

        ]

    }


    # =========================
    # SEND REQUEST
    # =========================

    response = requests.post(

        OPENROUTER_URL,

        headers=headers,

        json=data,

        timeout=60

    )


    # =========================
    # DEBUG
    # =========================

    print(
        "VISION STATUS:",
        response.status_code
    )

    print(
        "VISION RESPONSE:",
        response.text
    )


    # =========================
    # ERROR
    # =========================

    if response.status_code != 200:

        response.raise_for_status()


    # =========================
    # JSON
    # =========================

    result = response.json()


    if (
        "choices" not in result
        or not result["choices"]
    ):

        raise Exception(
            "Invalid Vision AI response."
        )


    # =========================
    # RETURN ANSWER
    # =========================

    return (
        result["choices"][0]
        ["message"]
        ["content"]
    )