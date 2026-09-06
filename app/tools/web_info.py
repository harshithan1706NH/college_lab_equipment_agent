import requests
from urllib.parse import quote


WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary"


def get_wikipedia_info(equipment_name):
    """
    Fetch general information about laboratory equipment
    from Wikipedia.
    """

    page_title = quote(
        equipment_name.strip().replace(" ", "_")
    )

    url = f"{WIKIPEDIA_API_URL}/{page_title}"

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "CollegeLabEquipmentAgent/1.0"
            },
            timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()

        return {
            "source": "Wikipedia",
            "title": data.get("title"),
            "description": data.get("description"),
            "information": data.get("extract"),
            "url": (
                data.get("content_urls", {})
                .get("desktop", {})
                .get("page")
            )
        }

    except requests.RequestException:
        return None


def get_web_search_info(equipment_name):
    """
    Fetch additional information from DuckDuckGo's
    public Instant Answer API.
    """

    url = "https://api.duckduckgo.com/"

    params = {
        "q": equipment_name,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers={
                "User-Agent": "CollegeLabEquipmentAgent/1.0"
            },
            timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()

        abstract = data.get("AbstractText")

        if not abstract:
            return None

        return {
            "source": "DuckDuckGo",
            "title": data.get("Heading"),
            "information": abstract,
            "url": data.get("AbstractURL")
        }

    except requests.RequestException:
        return None


def get_equipment_info(equipment_name):
    """
    Retrieve general web information about laboratory equipment.

    The function first attempts to retrieve information from
    Wikipedia and then attempts DuckDuckGo for additional
    information.

    This function does NOT access the college SQLite database.
    """

    if not equipment_name:

        return {
            "success": False,
            "message": "Equipment name is required."
        }


    equipment_name = equipment_name.strip()


    if not equipment_name:

        return {
            "success": False,
            "message": "Equipment name is required."
        }


    results = []


    # ---------------------------------------------------------
    # SOURCE 1: WIKIPEDIA
    # ---------------------------------------------------------

    wikipedia_result = get_wikipedia_info(
        equipment_name
    )

    if wikipedia_result:

        results.append(
            wikipedia_result
        )


    # ---------------------------------------------------------
    # SOURCE 2: DUCKDUCKGO
    # ---------------------------------------------------------

    duckduckgo_result = get_web_search_info(
        equipment_name
    )

    if duckduckgo_result:

        results.append(
            duckduckgo_result
        )


    # ---------------------------------------------------------
    # NO RESULTS
    # ---------------------------------------------------------

    if not results:

        return {
            "success": False,
            "equipment": equipment_name,
            "message": (
                f"No web information was found for "
                f"'{equipment_name}'."
            )
        }


    # ---------------------------------------------------------
    # COMBINE RESULTS
    # ---------------------------------------------------------

    return {
        "success": True,
        "equipment": equipment_name,
        "sources": results
    }