import json
import os
import requests

from dotenv import load_dotenv

from app.tools.equipment import (
    search_equipment,
    check_availability
)

from app.tools.borrowing import (
    borrow_equipment,
    return_equipment,
    get_borrowing_status
)

from app.tools.notification import (
    get_notifications
)


load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Free model with tool-calling support
MODEL = "openrouter/free"


# =========================================================
# TOOLS GIVEN TO THE AI
# =========================================================

TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "search_equipment",
            "description": "Search for laboratory equipment by name or laboratory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the equipment"
                    },
                    "lab": {
                        "type": "string",
                        "description": "Name of the laboratory"
                    }
                }
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check the availability of laboratory equipment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the equipment"
                    },
                    "lab": {
                        "type": "string",
                        "description": "Name of the laboratory"
                    }
                },
                "required": ["name"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "borrow_equipment",
            "description": "Borrow laboratory equipment for a specified number of days.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID of the user borrowing the equipment"
                    },
                    "equipment_id": {
                        "type": "integer",
                        "description": "ID of the equipment"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of units to borrow"
                    },
                    "duration_days": {
                        "type": "integer",
                        "description": "Number of days the equipment is required"
                    }
                },
                "required": [
                    "user_id",
                    "equipment_id",
                    "quantity",
                    "duration_days"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "return_equipment",
            "description": "Return equipment that was previously borrowed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "borrowing_id": {
                        "type": "integer",
                        "description": "ID of the borrowing record"
                    }
                },
                "required": ["borrowing_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_borrowing_status",
            "description": "Get the borrowing records of a user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer"
                    },
                    "status": {
                        "type": "string",
                        "description": "Optional status such as Borrowed or Returned"
                    }
                },
                "required": ["user_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_notifications",
            "description": "Get notifications belonging to a user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer"
                    }
                },
                "required": ["user_id"]
            }
        }
    }
]


# =========================================================
# MAP AI TOOL NAMES TO PYTHON FUNCTIONS
# =========================================================

TOOL_FUNCTIONS = {

    "search_equipment": search_equipment,

    "check_availability": check_availability,

    "borrow_equipment": borrow_equipment,

    "return_equipment": return_equipment,

    "get_borrowing_status": get_borrowing_status,

    "get_notifications": get_notifications
}


# =========================================================
# EXECUTE A TOOL
# =========================================================

def execute_tool(tool_name, arguments):

    if tool_name not in TOOL_FUNCTIONS:

        return {
            "success": False,
            "message": f"Unknown tool: {tool_name}"
        }

    try:

        function = TOOL_FUNCTIONS[tool_name]

        result = function(**arguments)

        return result

    except Exception as e:

        return {
            "success": False,
            "message": f"Tool execution error: {str(e)}"
        }


# =========================================================
# RUN AI AGENT
# =========================================================

def run_agent(user_message, user_id=1):

    if not OPENROUTER_API_KEY:

        return "OpenRouter API key is not configured."

    messages = [

        {
            "role": "system",
            "content": f"""
You are the College Lab Equipment Management AI Agent.

You help students and laboratory staff manage college
laboratory equipment.

You can:

1. Search equipment
2. Check equipment availability
3. Borrow equipment
4. Return equipment
5. Check borrowing status
6. Check notifications

The current user's ID is {user_id}.

IMPORTANT RULES:

- Never invent equipment information.
- Never invent availability.
- Never invent borrowing records.
- Never invent due dates.
- Use the appropriate tool whenever actual database information
  is required.
- If the user wants to borrow equipment, first determine which
  equipment they mean and check availability.
- If the user has not specified a required value, ask them for it.
- Use the result returned by the tool when giving your answer.
- Keep responses clear and concise.
"""
        },

        {
            "role": "user",
            "content": user_message
        }
    ]


    # =====================================================
    # AGENT LOOP
    # =====================================================

    while True:

        response = requests.post(

            OPENROUTER_URL,

            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },

            json={
                "model": MODEL,
                "messages": messages,
                "tools": TOOLS,
                "tool_choice": "auto"
            },

            timeout=60
        )


        # =================================================
        # CHECK OPENROUTER RESPONSE
        # =================================================

        if response.status_code != 200:

            return (
                f"OpenRouter error "
                f"{response.status_code}: "
                f"{response.text}"
            )


        data = response.json()

        assistant_message = data["choices"][0]["message"]


        # Add AI message to conversation

        messages.append(assistant_message)


        # =================================================
        # AI DID NOT REQUEST A TOOL
        # =================================================

        if "tool_calls" not in assistant_message:

            return assistant_message.get(
                "content",
                "I couldn't generate a response."
            )


        # =================================================
        # AI REQUESTED ONE OR MORE TOOLS
        # =================================================

        for tool_call in assistant_message["tool_calls"]:

            tool_name = tool_call["function"]["name"]

            arguments = json.loads(
                tool_call["function"]["arguments"]
            )


            print(
                f"\n[Agent Tool Call]"
            )

            print(
                f"{tool_name}({arguments})"
            )


            # Execute Python function

            result = execute_tool(
                tool_name,
                arguments
            )


            print(
                f"[Tool Result]"
            )

            print(result)


            # Send result back to AI

            messages.append({

                "role": "tool",

                "tool_call_id": tool_call["id"],

                "content": json.dumps(result)

            })