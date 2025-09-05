import os
import webbrowser

import msal
from dotenv import load_dotenv


def get_access_token(application_id, client_secret, scopes):
    print(f"Attempting to get token with:")
    print(f"- Application ID: {'***' if application_id else 'None'}")
    print(f"- Scopes: {scopes}")

    if not application_id or not client_secret:
        raise ValueError("Missing application_id or client_secret")

    client = msal.ConfidentialClientApplication(
        client_id=application_id,
        client_credential=client_secret,
        authority="https://login.microsoftonline.com/consumers/",
    )

    # Check if there is a refresh token stored
    refresh_token = None
    if os.path.exists("refresh_token.txt"):
        with open("refresh_token.txt", "r") as file:
            refresh_token = file.read().strip()

    if refresh_token:
        print("Found refresh token, attempting to use it...")
        try:
            token_response = client.acquire_token_by_refresh_token(
                refresh_token, scopes=scopes
            )
            if token_response and "access_token" in token_response:
                print("Successfully got token using refresh token")
                return token_response["access_token"]
        except Exception as e:
            print(f"Error using refresh token: {e}")

    print("Starting interactive authentication...")
    auth_url = client.get_authorization_request_url(scopes=scopes)
    print(f"\nOpening URL: {auth_url[:60]}...")
    webbrowser.open(auth_url)

    authorization_code = input("Enter the authorization code: ")

    if not authorization_code:
        raise ValueError("Authorization code is empty")

    print("Getting token with authorization code...")
    token_response = client.acquire_token_by_authorization_code(
        code=authorization_code, scopes=scopes
    )

    if "access_token" in token_response:
        print("Successfully got new token")
        # Store the refresh token
        if "refresh_token" in token_response:
            with open("refresh_token.txt", "w") as file:
                file.write(token_response["refresh_token"])
        return token_response["access_token"]
    else:
        error = token_response.get("error_description", "Unknown error")
        raise Exception(f"Could not acquire access token: {error}")


if __name__ == "__main__":
    # When run directly, use environment variables
    load_dotenv()
    client_id = os.getenv("MICROSOFT_APPLICATION_ID")
    client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
    scopes = ["Mail.Read", "Mail.ReadWrite", "Mail.Send", "User.Read"]

    token = get_access_token(client_id, client_secret, scopes)
    print(token)
    print({"Authorization": f"Bearer {token}"})
