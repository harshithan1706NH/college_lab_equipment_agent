from datetime import datetime

from app.database.db import get_db_connection


def create_notification(
    user_id: int,
    message: str,
    notification_type: str
):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Check user exists
    cursor.execute(
        "SELECT id FROM users WHERE id = ?",
        (user_id,)
    )

    if not cursor.fetchone():
        connection.close()

        return {
            "success": False,
            "message": "User not found."
        }

    created_at = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO notifications
        (user_id, message, type, created_at, is_read)
        VALUES (?, ?, ?, ?, 0)
    """, (
        user_id,
        message,
        notification_type,
        created_at
    ))

    notification_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {
        "success": True,
        "notification_id": notification_id,
        "message": message,
        "type": notification_type,
        "created_at": created_at
    }


def get_notifications(user_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM notifications
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    notifications = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return notifications


def mark_notification_read(notification_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE notifications
        SET is_read = 1
        WHERE id = ?
    """, (notification_id,))

    if cursor.rowcount == 0:
        connection.close()

        return {
            "success": False,
            "message": "Notification not found."
        }

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Notification marked as read."
    }