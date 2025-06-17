# python test.py
import requests
import time

def send_data(url: str = 'http://localhost:5000', data: dict = None, isJSON: bool = True):
    """
    Send data to the data endpoint.
    
    :url: endpoint that the data is sent to
    :data: data that we will send to the server (dictionary -> JSON)
    """

    # Data that we will send
    if data:
        pass
    else:
        data = {
            "message": "Open only red then only yellow then only green",
            "history": [],
        }

    # Send POST request with JSON data
    if isJSON:
        response = requests.post(url, json = data)
    else:
        response = requests.post(url, data = data)
    return response

if __name__ == "__main__":
    root = "http://localhost:5000"

    url_auth = root + "/chatbot/vanilla"
    url_send_data = root + "/chatbot/bluetooth_processor"
    url_send_data = root + "/auth/register"

    data = {
        "message": "Turn every light on sequentially",
        "history": [],
    }
    data = {
        "username": "ceenen2302acs",
        "name": "ceenenasc",
        "email": "gialukhu2302@gmail.com",
        "password": "password",
        "retype_password": "password",
    }
    
    if True:
    # while True:
        # time.sleep(0.5)
        response = send_data(url = url_send_data, data = data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")