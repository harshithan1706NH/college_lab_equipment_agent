# College Lab Equipment AI Agent

An AI-powered laboratory equipment management system that allows users to interact with college lab equipment records through natural-language queries. The agent uses an LLM with tool calling to search equipment, check availability, manage borrowing and returns, and retrieve equipment information.

## Features

- **AI chat interface:** Process natural-language requests through an LLM-powered agent.
- **Equipment search:** Find equipment by name or laboratory.
- **Availability checking:** View equipment quantities and availability status.
- **Equipment management:** Add, update, and remove equipment records.
- **Borrowing management:** Record equipment borrowing, calculate due dates, and update available quantities.
- **Equipment returns:** Record returns and restore available quantities.
- **Borrowing history:** Retrieve borrowing records and filter by status.
- **Notifications:** Create, view, and mark notifications as read.
- **Laboratory information:** Retrieve the laboratories listed in the database.
- **Web-based equipment information:** Retrieve general equipment information from Wikipedia and DuckDuckGo.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| FastAPI | REST API development |
| OpenRouter | LLM access and tool calling |
| SQLite | Storage for users, equipment, borrowing records, and notifications |
| Pydantic | Request data validation |
| Requests | HTTP requests to the LLM API and external information sources |
| python-dotenv | Loading environment variables |

## How It Works

1. A user submits a natural-language request through the chat endpoint.
2. The AI agent sends the conversation to an LLM through OpenRouter.
3. When a tool is needed, the model selects a registered function and supplies its arguments.
4. The corresponding Python function executes the requested operation against the SQLite database or retrieves external equipment information.
5. The tool result is returned to the agent, which produces a response for the user.

## Database

The SQLite database contains four main tables:

- **Users:** Stores user names, email addresses, and roles.
- **Equipment:** Stores equipment names, categories, laboratories, total quantities, available quantities, and status.
- **Borrowings:** Stores borrowing dates, due dates, return dates, quantities, and borrowing status.
- **Notifications:** Stores user notifications, timestamps, types, and read status.

The application initializes the database and inserts sample users and equipment records when it starts.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Check whether the API is running |
| GET | `/equipment` | Search equipment by name or laboratory |
| GET | `/equipment/availability` | Check equipment availability |
| POST | `/equipment` | Add equipment |
| PUT | `/equipment/{equipment_id}` | Update equipment |
| DELETE | `/equipment/{equipment_id}` | Remove equipment |
| POST | `/borrow` | Borrow equipment |
| POST | `/return/{borrowing_id}` | Return borrowed equipment |
| GET | `/borrowings/{user_id}` | Retrieve a user's borrowing records |
| POST | `/notifications` | Create a notification |
| GET | `/notifications/{user_id}` | Retrieve a user's notifications |
| PUT | `/notifications/{notification_id}/read` | Mark a notification as read |
| POST | `/chat` | Send a natural-language request to the AI agent |

FastAPI also provides interactive API documentation through its Swagger UI.
