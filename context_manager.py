import tiktoken


def count_tokens(text):
    """
    Count the approximate number of tokens in a text.
    """

    encoding = tiktoken.get_encoding("cl100k_base")

    return len(
        encoding.encode(text)
    )


def manage_context(
    messages,
    max_tokens=4000
):
    """
    Keep recent messages while staying
    within the token limit.
    """

    if not messages:
        return []

    selected_messages = []
    total_tokens = 0

    # Start from the newest message
    for message in reversed(messages):

        content = message["content"]

        message_tokens = count_tokens(
            content
        )

        if total_tokens + message_tokens > max_tokens:
            break

        selected_messages.insert(
            0,
            message
        )

        total_tokens += message_tokens

    return selected_messages