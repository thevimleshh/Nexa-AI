import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def save_memory(user_id, memory_text):
    """
    Save a useful memory for a specific user.
    """

    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO memories (user_id, memory)
        VALUES (%s, %s)
        """,
        (user_id, memory_text)
    )

    connection.commit()

    cursor.close()
    connection.close()
def should_save_memory(message):
    """
    Check whether a user message contains
    information that may be useful to remember.
    """

    message_lower = message.lower()

    memory_phrases = [
        "my name is",
        "i am learning",
        "i'm learning",
        "i like",
        "i love",
        "i prefer",
        "remember that",
        "my favorite",
        "i work as",
        "i study",
        "my favorite colour",
        "my favorite songs"
    ]

    for phrase in memory_phrases:
        if phrase in message_lower:
            return True

    return False
def get_memories(user_id):
    """
    Get all saved memories for a specific user.
    """

    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT memory
        FROM memories
        WHERE user_id = %s
        ORDER BY id ASC
        """,
        (user_id,)
    )

    memories = cursor.fetchall()

    cursor.close()
    connection.close()

    return memories