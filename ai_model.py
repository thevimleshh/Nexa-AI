
import os
import json
import requests

from dotenv import load_dotenv

from prompts import SYSTEM_PROMPT
from tools.calculator import CALCULATOR_TOOL, calculate


# =================================================
# LOAD ENVIRONMENT
# =================================================

load_dotenv()


# =================================================
# OPENROUTER CONFIGURATION
# =================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

MODEL_NAME = "openrouter/free"


# =================================================
# MAIN AI FUNCTION
# =================================================

def get_ai_response(
    messages,
    temperature=0.7,
    memory_text=""
):

    # =================================================
    # STEP 1: CHECK API KEY
    # =================================================

    if not OPENROUTER_API_KEY:

        raise Exception(
            "OPENROUTER_API_KEY is missing "
            "in .env file."
        )


    # =================================================
    # STEP 2: REQUEST HEADERS
    # =================================================

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


    # =================================================
    # STEP 3: PREPARE SYSTEM + MEMORY + CHAT
    # =================================================

    request_messages = [

        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }

    ]


    # =================================================
    # STEP 4: ADD USER MEMORY
    # =================================================

    if memory_text:

        request_messages.append(

            {
                "role": "system",

                "content": (
                    "The following information is "
                    "remembered about the user:\n\n"

                    f"{memory_text}\n\n"

                    "Use this information when it is "
                    "relevant to the user's question. "

                    "Treat this as information provided "
                    "by the user. "

                    "Do not mention the memory system "
                    "unless the user asks about it."
                )
            }

        )


    # =================================================
    # STEP 5: ADD CONVERSATION HISTORY
    # =================================================

    request_messages.extend(
        messages
    )


    # =================================================
    # STEP 6: PREPARE AI REQUEST
    # =================================================

    data = {

        "model":
            MODEL_NAME,

        "temperature":
            temperature,

        "top_p":
            0.9,

        "tools": [

            CALCULATOR_TOOL

        ],

        "messages":
            request_messages
    }


    # =================================================
    # STEP 7: SEND REQUEST TO OPENROUTER
    # =================================================

    try:

        response = requests.post(

            OPENROUTER_URL,

            headers=headers,

            json=data,

            timeout=60
        )


    except requests.exceptions.Timeout:

        raise Exception(
            "Nexa AI took too long to respond. "
            "Please try again."
        )


    except requests.exceptions.RequestException as error:

        print(
            "OpenRouter connection error:",
            error
        )

        raise Exception(
            "Nexa AI could not connect to "
            "the AI server. Please check "
            "your internet connection."
        )


    # =================================================
    # STEP 8: CHECK RESPONSE STATUS
    # =================================================

    print(
        "STATUS:",
        response.status_code
    )


    if response.status_code != 200:

        print(
            "OpenRouter Response:",
            response.text
        )


        # ---------------------------------------------
        # INVALID API KEY
        # ---------------------------------------------

        if response.status_code == 401:

            raise Exception(
                "Invalid OpenRouter API key."
            )


        # ---------------------------------------------
        # RATE LIMIT
        # ---------------------------------------------

        if response.status_code == 429:

            raise Exception(
                "Nexa AI is temporarily busy. "
                "Please try again in a moment."
            )


        # ---------------------------------------------
        # SERVER ERROR
        # ---------------------------------------------

        if response.status_code >= 500:

            raise Exception(
                "The AI server is temporarily "
                "unavailable. Please try again later."
            )


        # ---------------------------------------------
        # OTHER ERROR
        # ---------------------------------------------

        raise Exception(
            f"AI request failed with HTTP "
            f"{response.status_code}."
        )


    # =================================================
    # STEP 9: CONVERT RESPONSE TO JSON
    # =================================================

    try:

        result = response.json()

    except ValueError:

        raise Exception(
            "Nexa AI returned an invalid response."
        )


    # =================================================
    # STEP 10: CHECK CHOICES
    # =================================================

    if (

        "choices" not in result

        or not result["choices"]

    ):

        raise Exception(
            "Nexa AI returned an empty response."
        )


    # =================================================
    # STEP 11: GET ASSISTANT MESSAGE
    # =================================================

    assistant_message = (

        result["choices"][0]["message"]

    )


    print(
        "ASSISTANT MESSAGE:",
        assistant_message
    )


    # =================================================
    # STEP 12: CHECK TOOL CALLS
    # =================================================

    tool_calls = (

        assistant_message.get(
            "tool_calls"
        )

    )


    # =================================================
    # STEP 13: NORMAL AI RESPONSE
    # =================================================

    if not tool_calls:

        final_answer = (

            assistant_message.get(
                "content",
                ""
            )

        )


        if not final_answer:

            raise Exception(
                "Nexa AI returned an empty answer."
            )


        print(
            "AI TEXT:",
            final_answer
        )


        return final_answer


    # =================================================
    # STEP 14: ADD ASSISTANT TOOL MESSAGE
    # =================================================

    request_messages.append(

        assistant_message

    )


    # =================================================
    # STEP 15: EXECUTE TOOLS
    # =================================================

    for tool_call in tool_calls:

        function_name = (

            tool_call[
                "function"
            ][
                "name"
            ]

        )


        arguments_string = (

            tool_call[
                "function"
            ][
                "arguments"
            ]

        )


        print(
            "TOOL NAME:",
            function_name
        )


        print(
            "TOOL ARGUMENTS:",
            arguments_string
        )


        # =================================================
        # CONVERT ARGUMENTS FROM JSON
        # =================================================

        try:

            arguments = json.loads(
                arguments_string
            )

        except json.JSONDecodeError:

            raise Exception(
                "AI returned invalid tool arguments."
            )


        # =================================================
        # CALCULATOR TOOL
        # =================================================

        if function_name == "calculate":

            tool_result = calculate(

                arguments["a"],

                arguments["b"],

                arguments["operation"]

            )


        else:

            tool_result = (

                f"Unknown tool: {function_name}"

            )


        print(
            "TOOL RESULT:",
            tool_result
        )


        # =================================================
        # ADD TOOL RESULT TO CONVERSATION
        # =================================================

        request_messages.append(

            {

                "role":
                    "tool",

                "tool_call_id":
                    tool_call["id"],

                "content":
                    str(tool_result)

            }

        )


    # =================================================
    # STEP 16: PREPARE FINAL AI REQUEST
    # =================================================

    final_data = {

        "model":
            MODEL_NAME,

        "temperature":
            temperature,

        "top_p":
            0.9,

        "messages":
            request_messages
    }


    # =================================================
    # STEP 17: SEND FINAL REQUEST
    # =================================================

    try:

        final_response = requests.post(

            OPENROUTER_URL,

            headers=headers,

            json=final_data,

            timeout=60
        )


    except requests.exceptions.Timeout:

        raise Exception(
            "Nexa AI took too long to "
            "generate the final answer."
        )


    except requests.exceptions.RequestException as error:

        print(
            "Final OpenRouter connection error:",
            error
        )

        raise Exception(
            "Nexa AI could not connect to "
            "the AI server."
        )


    # =================================================
    # STEP 18: CHECK FINAL RESPONSE
    # =================================================

    print(
        "FINAL STATUS:",
        final_response.status_code
    )


    if final_response.status_code != 200:

        print(
            "Final OpenRouter Response:",
            final_response.text
        )


        if final_response.status_code == 429:

            raise Exception(
                "Nexa AI is temporarily busy. "
                "Please try again."
            )


        raise Exception(
            f"Final AI request failed with HTTP "
            f"{final_response.status_code}."
        )


    # =================================================
    # STEP 19: CONVERT FINAL RESPONSE TO JSON
    # =================================================

    try:

        final_result = (
            final_response.json()
        )

    except ValueError:

        raise Exception(
            "Nexa AI returned an invalid "
            "final response."
        )


    # =================================================
    # STEP 20: CHECK FINAL CHOICES
    # =================================================

    if (

        "choices" not in final_result

        or not final_result["choices"]

    ):

        raise Exception(
            "Nexa AI returned an empty "
            "final response."
        )


    # =================================================
    # STEP 21: EXTRACT FINAL ANSWER
    # =================================================

    final_answer = (

        final_result["choices"][0]
        ["message"]
        .get(
            "content",
            ""
        )

    )


    # =================================================
    # STEP 22: CHECK FINAL ANSWER
    # =================================================

    if not final_answer:

        raise Exception(
            "Nexa AI returned an empty "
            "final answer."
        )


    # =================================================
    # STEP 23: RETURN FINAL ANSWER
    # =================================================

    print(
        "FINAL AI ANSWER:",
        final_answer
    )


    return final_answer

