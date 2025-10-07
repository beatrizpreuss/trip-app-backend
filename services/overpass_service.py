import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
UA = {"User-Agent": "osm-query-from-form/1.0"}


def fetch_overpass_results(query: str) -> dict:
    """
    Send a query to Overpass API and return the JSON result.
    Handles request errors and timeouts.
    """
    try:
        res = requests.get(OVERPASS_URL, params={"data": query}, headers=UA, timeout=180)
        res.raise_for_status()
    except requests.exceptions.Timeout:
        return {"error": "Overpass request timed out"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Overpass request failed: {e}"}

    try:
        return res.json()
    except ValueError:
        return {"error": "Failed to parse JSON from Overpass response"}