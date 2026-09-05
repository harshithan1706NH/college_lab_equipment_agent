from app.database.db import get_db_connection


def add_equipment(
    name: str,
    category: str,
    lab: str,
    quantity: int
):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO equipment
        (name, category, lab, quantity, available_quantity, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        category,
        lab,
        quantity,
        quantity,
        "Working"
    ))

    equipment_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {
        "success": True,
        "equipment_id": equipment_id,
        "message": f"{quantity} {name}(s) added successfully."
    }


def search_equipment(name: str = None, lab: str = None):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM equipment WHERE 1=1"
    parameters = []

    if name:
        query += " AND LOWER(name) LIKE LOWER(?)"
        parameters.append(f"%{name}%")

    if lab:
        query += " AND LOWER(lab) LIKE LOWER(?)"
        parameters.append(f"%{lab}%")

    cursor.execute(query, parameters)

    equipment = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return equipment


def check_availability(name: str, lab: str = None):
    equipment = search_equipment(name, lab)

    if not equipment:
        return {
            "found": False,
            "message": f"No equipment named '{name}' was found."
        }

    return {
        "found": True,
        "equipment": equipment
    }


def update_equipment(
    equipment_id: int,
    quantity: int = None,
    status: str = None
):
    connection = get_db_connection()
    cursor = connection.cursor()

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

    updates = []
    parameters = []

    if quantity is not None:
        borrowed_quantity = (
            equipment["quantity"] -
            equipment["available_quantity"]
        )

        if quantity < borrowed_quantity:
            connection.close()

            return {
                "success": False,
                "message": (
                    f"Cannot reduce quantity below "
                    f"{borrowed_quantity}; equipment is currently borrowed."
                )
            }

        new_available_quantity = quantity - borrowed_quantity

        updates.append("quantity = ?")
        parameters.append(quantity)

        updates.append("available_quantity = ?")
        parameters.append(new_available_quantity)

    if status is not None:
        updates.append("status = ?")
        parameters.append(status)

    if not updates:
        connection.close()

        return {
            "success": False,
            "message": "No changes were provided."
        }

    parameters.append(equipment_id)

    cursor.execute(
        f"""
        UPDATE equipment
        SET {", ".join(updates)}
        WHERE id = ?
        """,
        parameters
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Equipment updated successfully."
    }


def remove_equipment(equipment_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

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

    if equipment["available_quantity"] != equipment["quantity"]:
        connection.close()

        return {
            "success": False,
            "message": "Cannot remove equipment while some units are borrowed."
        }

    cursor.execute(
        "DELETE FROM equipment WHERE id = ?",
        (equipment_id,)
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Equipment removed successfully."
    }