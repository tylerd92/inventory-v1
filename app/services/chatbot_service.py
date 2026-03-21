from openai import OpenAI
import json
from app.services.inventory_service import get_inventory_by_product_name
from app.db.session import get_db
from app.core.config import settings

client = None  # Module-level client; initialized lazily and replaceable in tests


def _get_openai_client():
    """Get OpenAI client with proper configuration."""
    global client
    if client is None:
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY environment variable.")
        client = OpenAI(api_key=settings.openai_api_key)
    return client

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_inventory_by_product_name",
            "description": "Get inventory count for a product by its name",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "Name of the product"
                    }
                },
                "required": ["product_name"]
            }
        }
    }
]


def process_chat(message: str):
    _client = _get_openai_client()

    response = _client.chat.completions.create(
        model="gpt-3.5-turbo",  # Using a more common model
        messages=[
            {"role": "system", "content": "You are an AI inventory assistant."},
            {"role": "user", "content": message}
        ],
        tools=tools,
        tool_choice="auto"
    )

    msg = response.choices[0].message

    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if function_name == "get_inventory_by_product_name":
            product_name = arguments["product_name"]
            # Get database session
            db = next(get_db())
            try:
                quantity = get_inventory_by_product_name(db, product_name)
            finally:
                db.close()

            # Send function result back to model for natural response
            second_response = _client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using a more common model
                messages=[
                    {"role": "system", "content": "You are an AI inventory assistant."},
                    {"role": "user", "content": message},
                    msg,
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(quantity)
                    }
                ]
            )

            return second_response.choices[0].message.content

    return msg.content