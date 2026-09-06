from app.database.db import get_db_connection


def add_equipment(name, category, lab, quantity):
    if not name or not lab:
        return {
            "success": False,
            "message": "Equipment name and lab are required."
        }

    if quantity <= 0:
        return {
            "success": False,
            "message": "Quantity must be greater than 0."
        }

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO equipment (
            name,
            category,
            lab,
            quantity,
            available_quantity,
            status
        )
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
        "message": f"{name} added successfully.",
        "equipment_id": equipment_id
    }


def search_equipment(name=None, lab=None):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            id,
            name,
            category,
            lab,
            quantity,
            available_quantity,
            status
        FROM equipment
        WHERE 1=1
    """

    parameters = []

    if name:
        query += " AND LOWER(name) LIKE LOWER(?)"
        parameters.append(f"%{name}%")

    if lab:
        query += " AND LOWER(lab) LIKE LOWER(?)"
        parameters.append(f"%{lab}%")

    query += " ORDER BY lab, name"

    cursor.execute(query, parameters)

    equipment = [dict(row) for row in cursor.fetchall()]

    connection.close()

    if not equipment:
        return {
            "success": False,
            "message": "No equipment found."
        }

    return {
        "success": True,
        "equipment": equipment
    }


def check_availability(name, lab=None):
    if not name:
        return {
            "success": False,
            "message": "Equipment name is required."
        }

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            id,
            name,
            lab,
            quantity,
            available_quantity,
            status
        FROM equipment
        WHERE LOWER(name) LIKE LOWER(?)
    """

    parameters = [f"%{name}%"]

    if lab:
        query += " AND LOWER(lab) LIKE LOWER(?)"
        parameters.append(f"%{lab}%")

    cursor.execute(query, parameters)

    equipment = [dict(row) for row in cursor.fetchall()]

    connection.close()

    if not equipment:
        return {
            "success": False,
            "message": f"No equipment found for '{name}'."
        }

    return {
        "success": True,
        "equipment": equipment
    }


def get_labs():
    """
    Return all labs present in the equipment database.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            lab,
            COUNT(*) AS equipment_types
        FROM equipment
        GROUP BY lab
        ORDER BY lab
    """)

    labs = [dict(row) for row in cursor.fetchall()]

    connection.close()

    if not labs:
        return {
            "success": False,
            "message": "No labs found in the database."
        }

    return {
        "success": True,
        "total_labs": len(labs),
        "labs": labs
    }


def update_equipment(equipment_id, quantity=None, status=None):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            quantity,
            available_quantity
        FROM equipment
        WHERE id = ?
    """, (equipment_id,))

    equipment = cursor.fetchone()

    if not equipment:
        connection.close()

        return {
            "success": False,
            "message": "Equipment not found."
        }

    current_quantity = equipment["quantity"]
    current_available = equipment["available_quantity"]

    if quantity is not None:

        if quantity <= 0:
            connection.close()

            return {
                "success": False,
                "message": "Quantity must be greater than 0."
            }

        borrowed_quantity = current_quantity - current_available

        if quantity < borrowed_quantity:
            connection.close()

            return {
                "success": False,
                "message": (
                    "Quantity cannot be reduced below the number "
                    "of currently borrowed units."
                )
            }

        new_available_quantity = quantity - borrowed_quantity

        cursor.execute("""
            UPDATE equipment
            SET quantity = ?,
                available_quantity = ?
            WHERE id = ?
        """, (
            quantity,
            new_available_quantity,
            equipment_id
        ))

    if status is not None:

        cursor.execute("""
            UPDATE equipment
            SET status = ?
            WHERE id = ?
        """, (
            status,
            equipment_id
        ))

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Equipment updated successfully."
    }


def remove_equipment(equipment_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            quantity,
            available_quantity
        FROM equipment
        WHERE id = ?
    """, (equipment_id,))

    equipment = cursor.fetchone()

    if not equipment:
        connection.close()

        return {
            "success": False,
            "message": "Equipment not found."
        }

    borrowed_quantity = (
        equipment["quantity"]
        - equipment["available_quantity"]
    )

    if borrowed_quantity > 0:
        connection.close()

        return {
            "success": False,
            "message": (
                "Equipment cannot be removed because "
                "some units are currently borrowed."
            )
        }

    cursor.execute("""
        DELETE FROM equipment
        WHERE id = ?
    """, (equipment_id,))

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Equipment removed successfully."
    }