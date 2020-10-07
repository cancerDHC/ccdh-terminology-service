import requests
import json


def search_term(term: str, options: str = 'partial'):
    endpoint = 'https://gdc-mvs.nci.nih.gov/gdc/search/all/p'
    params = {
        'keyword': term,
        'options': options
    }
    url = "https://gdc-mvs.nci.nih.gov/gdc/search/all/p?keyword=cfDNA&options=partial"

    payload = {}
    headers = {}

    response = requests.request("GET", endpoint, headers=headers, data=payload, params=params)

    print(response.text.encode('utf8'))
    resp_obj = response.json()
    return resp_obj