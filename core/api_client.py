import requests


class APIClient:

    def __init__(self, url, timeout=5):

        self.url = url
        self.timeout = timeout

    def send_plate(self, payload):

        response = requests.post(
            self.url,
            json=payload,
            timeout=self.timeout
        )

        response.raise_for_status()

        return response.json()