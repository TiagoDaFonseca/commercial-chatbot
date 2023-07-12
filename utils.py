from requests_html import HTMLSession
import openai
import json
import requests


def scrape_info_from(url: str) -> str:
    """
    Scrape information from url provided
    returns: string
    """
    s = HTMLSession()
    r = s.get(url)
    divp = r.html.find('h2,h3,h4,h5,h6,p,a,span')
    return '\n'.join([d.text for d in divp])


def get_completion_from(messages, model='gpt-3.5-turbo', temperature=0, max_tokens=500):
    """
    Openai chat completion request
    returns: string
    """
    response = openai.ChatCompletion.create(model=model, messages=messages, temperature=0, max_tokens=max_tokens)
    return response.choices[0].message['content']


def get_city(prompt: str) -> (str, str):
    """
    Checks if user prompt mentions a city
    returns: tuple (boolean, string)
    """
    messages = [{'role': 'user', 'content': f' provide in json format if the sentence between ### \
                                            mention a city (city_check = true/false) and the name of the city \
                                            (city_name=city). If there is no city resolve to None:###{prompt}###'
                 }]
    response = get_completion_from(messages)
    r = json.loads(response)
    return r['city_check'], r['city_name']


def get_weather(city) -> dict:
    """
    Weather API service
    returns: json
    """
    url = f'https://weather-api-by-any-city.p.rapidapi.com/weather/{city}'
    headers = {
        "X-RapidAPI-Key": "3cc9b2533dmshe5f859e07cf719ap12b21ajsne7a51c643f12",
        "X-RapidAPI-Host": "weather-api-by-any-city.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers).json()
    return response
