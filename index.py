import requests
from bs4 import BeautifulSoup

def download(url):
    try:

        response = requests.get(url)
        response.raise_for_status()
        print(response.__dict__)

        with open('audio.wav', 'wb') as file:
          file.write(response.content)
        print("file downloaded as")

    except Exception as e:
        print("An error occurred:", str(e))
        return None

url_to_scrape = "https://profitpro-audio.s3.amazonaws.com/audio.2023-08-18%2015%3A39%3A35.5.wav?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAQCDTSTHPE4QDOJGG%2F20230818%2Feu-north-1%2Fs3%2Faws4_request&X-Amz-Date=20230818T153940Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=bf59af77a3f9f57fd4548cc6206d7466c4263a2013a23f51fd57f1b2eced96d5"  # Replace with your desired URL

download(url_to_scrape)
