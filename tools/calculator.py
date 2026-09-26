def calculate(a, b, operation):
    """
    Perform a basic mathematical operation.
    """

    if operation == "add":
        return a + b

    elif operation == "subtract":
        return a - b

    elif operation == "multiply":
        return a * b

    elif operation == "divide":

        if b == 0:
            return "Cannot divide by zero"

        return a / b

    else:
        return "Unknown operation"


CALCULATOR_TOOL = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Perform basic mathematical calculations.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "First number"
                },
                "b": {
                    "type": "number",
                    "description": "Second number"
                },
                "operation": {
                    "type": "string",
                    "enum": [
                        "add",
                        "subtract",
                        "multiply",
                        "divide"
                    ],
                    "description": "Mathematical operation"
                }
            },
            "required": [
                "a",
                "b",
                "operation"
            ]
        }
    }
}