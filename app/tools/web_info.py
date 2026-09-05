import requests
from urllib.parse import quote


def get_equipment_info(equipment_name):
    """
    Fetch general information about laboratory equipment
    from Wikipedia's public web API.
    """

    if not equipment_name:
        return {
            "success": False,
            "message": "Equipment name is required."
        }

    # Convert equipment name into a Wikipedia page URL
    page_title = quote(equipment_name.strip().replace(" ", "_"))

    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title}"

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "CollegeLabEquipmentAgent/1.0"
            },
            timeout=10
        )

        if response.status_code != 200:
            return {
                "success": False,
                "message": f"No web information found for '{equipment_name}'."
            }

        data = response.json()

        return {
            "success": True,
            "equipment": equipment_name,
            "title": data.get("title"),
            "description": data.get("description"),
            "information": data.get("extract"),
            "source": data.get("content_urls", {})
                .get("desktop", {})
                .get("page")
        }

    except requests.RequestException as e:
        return {
            "success": False,
            "message": f"Unable to fetch web information: {str(e)}"
        }