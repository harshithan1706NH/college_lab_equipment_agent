import json
import os
import requests

from dotenv import load_dotenv

from app.tools.web_info import get_equipment_info

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

MODEL = "openrouter/free"



CONVERSATION_MEMORY = {}




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
            "description": "Check the availability of laboratory equipment from the college database.",
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
            "name": "get_equipment_info",
            "description": "Get general information, meaning, purpose, and usage of laboratory equipment from the web.",
            "parameters": {
                "type": "object",
                "properties": {
                    "equipment_name": {
                        "type": "string",
                        "description": "Name of the laboratory equipment"
                    }
                },
                "required": ["equipment_name"]
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




TOOL_FUNCTIONS = {

    "search_equipment": search_equipment,

    "check_availability": check_availability,

    "get_equipment_info": get_equipment_info,

    "borrow_equipment": borrow_equipment,

    "return_equipment": return_equipment,

    "get_borrowing_status": get_borrowing_status,

    "get_notifications": get_notifications

}



SYSTEM_PROMPT = """
You are the College Lab Equipment Management AI Agent.

You help students and laboratory staff manage college
laboratory equipment.

You can:

1. Search equipment
2. Check equipment availability
3. Get general equipment information from the web
4. Borrow equipment
5. Return equipment
6. Check borrowing status
7. Check notifications


IMPORTANT RULES:

- Never invent equipment information.
- Never invent availability.
- Never invent borrowing records.
- Never invent due dates.

- Use the appropriate database tool whenever actual
  college-specific information is required.

- Use get_equipment_info when the user asks:
  - what an equipment item is
  - what it does
  - what it is used for
  - how it is generally used
  - for general information about the equipment

- Use database tools for college-specific information such as:
  - quantity
  - available quantity
  - laboratory location
  - equipment status
  - borrowing records
  - due dates

- Do not use web information to determine college inventory
  or availability.

- Use previous conversation context to understand references
  such as "it", "one", "that equipment", "the same item", etc.

- If the user has already identified an equipment item in the
  conversation, remember it and use that equipment when the
  user refers to it later.

- Correct obvious small typing mistakes when the intended
  meaning is clear from the conversation.

- If the user wants to borrow equipment, determine the
  equipment from the current conversation before asking them
  to repeat it.

- If a required value such as quantity or duration is genuinely
  missing, ask the user for that value.

- Use the result returned by the tool when giving your answer.

- Keep responses clear and concise.
"""



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


def run_agent(user_message, user_id=1):

    if not OPENROUTER_API_KEY:

        return "OpenRouter API key is not configured."



    if user_id not in CONVERSATION_MEMORY:

        CONVERSATION_MEMORY[user_id] = [

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }

        ]


    messages = CONVERSATION_MEMORY[user_id]


  

    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )




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



        if response.status_code != 200:

            return (
                f"OpenRouter error "
                f"{response.status_code}: "
                f"{response.text}"
            )


        data = response.json()

        assistant_message = data["choices"][0]["message"]


        

        messages.append(assistant_message)


     

        if "tool_calls" not in assistant_message:

            return assistant_message.get(
                "content",
                "I couldn't generate a response."
            )


      

        for tool_call in assistant_message["tool_calls"]:

            tool_name = tool_call["function"]["name"]

            arguments = json.loads(
                tool_call["function"]["arguments"]
            )


            print("\n[Agent Tool Call]")

            print(
                f"{tool_name}({arguments})"
            )


            
           

            result = execute_tool(
                tool_name,
                arguments
            )


            print("[Tool Result]")

            print(result)


           

            messages.append({

                "role": "tool",

                "tool_call_id": tool_call["id"],

                "content": json.dumps(result)

            })