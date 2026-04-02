import requests
from bs4 import BeautifulSoup

def get_exim_rates(date):
    url = "https://eximindiaonline.in:4000/forexes/get_forexes_website"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://eximin.net",
    }

    payload = {"date" : date}

    response = requests.post(url, json=payload, headers=headers)

    print(response.status_code)
    print(response.json())
    
    return response.json()