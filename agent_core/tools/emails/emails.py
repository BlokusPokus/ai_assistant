import os
from dotenv import load_dotenv
from ms_graph import get_access_token
import httpx

MS_GRAPH_API_URL = "https://graph.microsoft.com/v1.0"


def main():
    load_dotenv()
    APPLICATION_ID = os.getenv("MICROSOFT_APPLICATION_ID")
    CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")
    SCOPES = ['User.read', 'Mail.ReadWrite', ]

    endpoint = f'{MS_GRAPH_API_URL}/me/messages'

    try:
        access_token = get_access_token(
            APPLICATION_ID, CLIENT_SECRET, SCOPES)
        print(access_token)

        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        for i in range(0, 4, 2):
            params = {
                '$top': 2,
                '$select': '*',
                '$skip': i,
                '$orderby': 'receivedDateTime desc'
            }
            response = httpx.get(endpoint, headers=headers, params=params)
            if response.status_code != 200:
                raise Exception(f"Failed to get messages: {response.text}")

            json_response = response.json()
            print(json_response)

            for mail in json_response.get('value', []):
                if mail['isDraft']:
                    pass
                print(mail['subject'])
                print(mail['bodyPreview'])
                print(mail['receivedDateTime'])
                print(mail['from']['emailAddress']['name'])
                print(mail['from']['emailAddress']['address'])
            print('-' * 100)
    except Exception as e:
        print(e)


main()
