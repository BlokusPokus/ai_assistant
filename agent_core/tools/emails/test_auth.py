from dotenv import load_dotenv
import os


def test_auth():
    load_dotenv()

    # Get and verify environment variables
    app_id = os.getenv("MICROSOFT_APPLICATION_ID")
    client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")

    print("Environment variables loaded:")
    print(f"App ID exists: {bool(app_id)}")
    print(f"Client Secret exists: {bool(client_secret)}")

    if not app_id or not client_secret:
        print("Missing required environment variables!")
        return

    # Try authentication
    from ms_graph import get_access_token

    scopes = ['Mail.Read']  # Minimal scope for testing

    try:
        token = get_access_token(app_id, client_secret, scopes)
        print("Authentication successful!")
        print(f"Token (first 10 chars): {token[:10]}...")
    except Exception as e:
        print(f"Authentication failed: {str(e)}")


if __name__ == "__main__":
    test_auth()
