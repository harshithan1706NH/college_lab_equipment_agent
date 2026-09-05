from datetime import date, timedelta

from app.database.db import get_db_connection
from app.tools.notification import create_notification


def borrow_equipment(
    user_id: int,
    equipment_id: int,
    quantity: int,
    duration_days: int
):
    connection = get_db_connection()
    cursor = connection.cursor()

    # -----------------------------
    # Check user
    # -----------------------------
    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )

    user = cursor.fetchone()

    if not user:
        connection.close()

        return {
            "success": False,
            "message": "User not found."
        }

    # -----------------------------
    # Check equipment
    # -----------------------------
    cursor.execute(
        "SELECT * FROM equipment WHERE id = ?",
        (equipment_id,)
    )

    equipment = cursor.fetchone()

    if not equipment:
        connection.close()

        return {
            "success": False,
            "message": "Equipment not found."
        }

    # -----------------------------
    # Validate quantity
    # -----------------------------
    if quantity <= 0:
        connection.close()

        return {
            "success": False,
            "message": "Quantity must be greater than zero."
        }

    if quantity > equipment["available_quantity"]:
        connection.close()

        return {
            "success": False,
            "message": (
                f"Only {equipment['available_quantity']} "
                f"unit(s) of {equipment['name']} are available."
            )
        }

    # -----------------------------
    # Validate duration
    # -----------------------------
    if duration_days <= 0:
        connection.close()

        return {
            "success": False,
            "message": "Duration must be at least 1 day."
        }

    # -----------------------------
    # Calculate dates
    # -----------------------------
    borrow_date = date.today()

    due_date = borrow_date + timedelta(
        days=duration_days
    )

    # -----------------------------
    # Create borrowing record
    # -----------------------------
    cursor.execute("""
        INSERT INTO borrowings
        (
            user_id,
            equipment_id,
            quantity,
            borrow_date,
            due_date,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        equipment_id,
        quantity,
        borrow_date.isoformat(),
        due_date.isoformat(),
        "Borrowed"
    ))

    borrowing_id = cursor.lastrowid

    # -----------------------------
    # Decrease available quantity
    # -----------------------------
    cursor.execute("""
        UPDATE equipment
        SET available_quantity =
            available_quantity - ?
        WHERE id = ?
    """, (
        quantity,
        equipment_id
    ))

    # Save database changes
    connection.commit()

    connection.close()

    # -----------------------------
    # Create notification
    # -----------------------------
    create_notification(
        user_id=user_id,
        message=(
            f"Your {equipment['name']} is due on "
            f"{due_date.isoformat()}."
        ),
        notification_type="borrow_confirmation"
    )

    # -----------------------------
    # Return result
    # -----------------------------
    return {
        "success": True,
        "borrowing_id": borrowing_id,
        "equipment": equipment["name"],
        "quantity": quantity,
        "borrow_date": borrow_date.isoformat(),
        "due_date": due_date.isoformat(),
        "status": "Borrowed",
        "message": (
            f"{quantity} {equipment['name']}(s) "
            f"borrowed successfully. "
            f"Due date: {due_date.isoformat()}."
        )
    }


def return_equipment(borrowing_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    # -----------------------------
    # Find borrowing record
    # -----------------------------
    cursor.execute("""
        SELECT
            borrowings.*,
            equipment.name AS equipment_name
        FROM borrowings
        JOIN equipment
            ON borrowings.equipment_id = equipment.id
        WHERE borrowings.id = ?
    """, (borrowing_id,))

    borrowing = cursor.fetchone()

    if not borrowing:
        connection.close()

        return {
            "success": False,
            "message": "Borrowing record not found."
        }

    # -----------------------------
    # Check if already returned
    # -----------------------------
    if borrowing["status"] == "Returned":
        connection.close()

        return {
            "success": False,
            "message": "This equipment has already been returned."
        }

    # -----------------------------
    # Return date
    # -----------------------------
    return_date = date.today()

    # -----------------------------
    # Mark borrowing as returned
    # -----------------------------
    cursor.execute("""
        UPDATE borrowings
        SET
            return_date = ?,
            status = 'Returned'
        WHERE id = ?
    """, (
        return_date.isoformat(),
        borrowing_id
    ))

    # -----------------------------
    # Increase available quantity
    # -----------------------------
    cursor.execute("""
        UPDATE equipment
        SET available_quantity =
            available_quantity + ?
        WHERE id = ?
    """, (
        borrowing["quantity"],
        borrowing["equipment_id"]
    ))

    connection.commit()

    connection.close()

    # -----------------------------
    # Create return notification
    # -----------------------------
    create_notification(
        user_id=borrowing["user_id"],
        message=(
            f"Your {borrowing['equipment_name']} "
            f"has been returned successfully."
        ),
        notification_type="return_confirmation"
    )

    return {
        "success": True,
        "borrowing_id": borrowing_id,
        "equipment": borrowing["equipment_name"],
        "quantity": borrowing["quantity"],
        "return_date": return_date.isoformat(),
        "status": "Returned",
        "message": (
            f"{borrowing['equipment_name']} "
            f"returned successfully."
        )
    }


def get_borrowing_status(
    user_id: int,
    status: str = None
):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            borrowings.id,
            users.name AS user_name,
            equipment.name AS equipment_name,
            equipment.lab,
            borrowings.quantity,
            borrowings.borrow_date,
            borrowings.due_date,
            borrowings.return_date,
            borrowings.status
        FROM borrowings
        JOIN users
            ON borrowings.user_id = users.id
        JOIN equipment
            ON borrowings.equipment_id = equipment.id
        WHERE borrowings.user_id = ?
    """

    parameters = [user_id]

    # Optional status filter
    if status:
        query += """
            AND borrowings.status = ?
        """

        parameters.append(status)

    query += """
        ORDER BY borrowings.id DESC
    """

    cursor.execute(
        query,
        parameters
    )

    records = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return records