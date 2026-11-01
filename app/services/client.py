from app.config import API_TIMEOUT_SECONDS, EXTERNAL_API_URL
requests = EXTERNAL_API_URL


def get_external_data():
    try:
        response = requests.get(EXTERNAL_API_URL, timeout=API_TIMEOUT_SECONDS)
        response.raise_for_status()  #Raise an error for bad responses
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from external API: {e}")
        return None