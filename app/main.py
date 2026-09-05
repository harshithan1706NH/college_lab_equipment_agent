from fastapi import FastAPI
from pydantic import BaseModel

from app.agent import run_agent
from app.database.db import initialize_database, seed_database
from app.tools.equipment import (
    add_equipment,
    search_equipment,
    check_availability,
    update_equipment,
    remove_equipment
)
from app.tools.borrowing import (
    borrow_equipment,
    return_equipment,
    get_borrowing_status
)
from app.tools.notification import (
    create_notification,
    get_notifications,
    mark_notification_read
)

app = FastAPI(
    title="College Lab Equipment AI Agent",
    version="1.0.0"
)


@app.on_event("startup")
def startup():
    initialize_database()
    seed_database()


@app.get("/")
def root():
    return {
        "message": "College Lab Equipment AI Agent is running"
    }


@app.get("/equipment")
def get_equipment(
    name: str = None,
    lab: str = None
):
    return search_equipment(name, lab)


@app.get("/equipment/availability")
def equipment_availability(
    name: str,
    lab: str = None
):
    return check_availability(name, lab)


@app.post("/equipment")
def create_equipment(
    name: str,
    category: str,
    lab: str,
    quantity: int
):
    return add_equipment(name, category, lab, quantity)


@app.put("/equipment/{equipment_id}")
def modify_equipment(
    equipment_id: int,
    quantity: int = None,
    status: str = None
):
    return update_equipment(
        equipment_id,
        quantity,
        status
    )


@app.delete("/equipment/{equipment_id}")
def delete_equipment(equipment_id: int):
    return remove_equipment(equipment_id)

@app.post("/borrow")
def borrow(
    user_id: int,
    equipment_id: int,
    quantity: int,
    duration_days: int
):
    return borrow_equipment(
        user_id,
        equipment_id,
        quantity,
        duration_days
    )


@app.post("/return/{borrowing_id}")
def return_borrowing(borrowing_id: int):
    return return_equipment(borrowing_id)


@app.get("/borrowings/{user_id}")
def borrowing_status(
    user_id: int,
    status: str = None
):
    return get_borrowing_status(
        user_id,
        status
    )

@app.post("/notifications")
def create_notification_endpoint(
    user_id: int,
    message: str,
    notification_type: str
):
    return create_notification(
        user_id,
        message,
        notification_type
    )


@app.get("/notifications/{user_id}")
def get_user_notifications(user_id: int):
    return get_notifications(user_id)


@app.put("/notifications/{notification_id}/read")
def read_notification(notification_id: int):
    return mark_notification_read(notification_id)

class ChatRequest(BaseModel):
    message: str
    user_id: int = 1


@app.post("/chat")
def chat(request: ChatRequest):

    response = run_agent(
        request.message,
        request.user_id
    )

    return {
        "response": response
    }