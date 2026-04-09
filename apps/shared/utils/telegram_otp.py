import requests

from arena.settings import TELEGRAM_GATEWAY_URL, TELEGRAM_GATEWAY_TOKEN

TOKEN = TELEGRAM_GATEWAY_TOKEN
PHONE = '+998932543733'
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

def post_request_status(endpoint, json_body):
    url = f"{TELEGRAM_GATEWAY_URL}{endpoint}"
    response = requests.post(url, headers=HEADERS, json=json_body)
    if response.status_code == 200:
        response_json = response.json()
        if response_json.get('ok'):
            res = response_json.get('result', {})
            return res
        else:
            error_message = response_json.get('error', 'Unknown error')
            print(f"Error: {error_message}")
            return None
    else:
        print(f"Failed to get request status: HTTP {response.status_code}")
        return None
