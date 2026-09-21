"""
Setup Helper: Generate Google Blogger API OAuth2 Refresh Token in 60 seconds.

Usage:
    python setup_blogger_auth.py
"""

import os
import sys
import glob
from pathlib import Path
from dotenv import load_dotenv

# Ensure UTF-8 console with line buffering
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

SCOPES = [
    "https://www.googleapis.com/auth/blogger"
]

def update_env_file(updates):
    if not ENV_PATH.exists():
        content = ""
    else:
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            content = f.read()

    for key, value in updates.items():
        line_prefix = f"{key}="
        if line_prefix in content:
            lines = content.splitlines()
            new_lines = []
            for line in lines:
                if line.startswith(line_prefix):
                    new_lines.append(f"{key}={value}")
                else:
                    new_lines.append(line)
            content = "\n".join(new_lines)
        else:
            content += f"\n{key}={value}"

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

def main():
    print("=" * 65)
    print("🔐 GPT-TYPE Google Blogger API Authentication Assistant")
    print("=" * 65)

    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    # Check for downloaded client_secret*.json file
    json_files = list(BASE_DIR.glob("client_secret*.json"))
    if json_files:
        selected_json = json_files[0]
        print(f"✅ Found downloaded Google credentials file: {selected_json.name}")
        flow = InstalledAppFlow.from_client_secrets_file(str(selected_json), scopes=SCOPES)
        client_id = flow.client_config.get("client_id", "")
        client_secret = flow.client_config.get("client_secret", "")
    else:
        env_client_id = os.getenv("BLOGGER_CLIENT_ID", "").strip()
        env_client_secret = os.getenv("BLOGGER_CLIENT_SECRET", "").strip()

        if env_client_id and env_client_secret:
            print("✅ Loaded existing BLOGGER_CLIENT_ID and BLOGGER_CLIENT_SECRET from .env")
            client_id = env_client_id
            client_secret = env_client_secret
        else:
            client_id = input("\nEnter your OAuth Client ID (paste here): ").strip()
            client_secret = input("Enter your OAuth Client Secret (paste here): ").strip()

        if not client_id or not client_secret:
            print("❌ Error: Client ID and Client Secret are required!")
            sys.exit(1)

        client_config = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:8080/"]
            }
        }
        flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)

    class AuthUrlPrompt:
        def __init__(self, base_dir):
            self.base_dir = base_dir

        def format(self, **kwargs):
            url = kwargs.get("url", "")
            scratch_dir = self.base_dir / "scratch"
            scratch_dir.mkdir(parents=True, exist_ok=True)
            with open(scratch_dir / "auth_url.txt", "w", encoding="utf-8") as f:
                f.write(url.strip())
            with open(scratch_dir / "auth.html", "w", encoding="utf-8") as f:
                f.write(f'<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0; url={url}"></head><body><h2>Connecting to Google Sign-In...</h2><p><a href="{url}">Click here if not redirected automatically</a></p></body></html>')

            import subprocess
            try:
                subprocess.Popen(f'start "" "{url}"', shell=True)
            except Exception:
                pass

            output = (
                "\n" + "=" * 70 + "\n"
                "👉 GOOGLE SIGN-IN URL:\n"
                f"{url}\n"
                + "=" * 70 + "\n"
            )
            return output

    try:
        print("\n🌐 Starting local authorization server...")
        import time
        import wsgiref.simple_server
        import wsgiref.util
        from google_auth_oauthlib.flow import _ExclusiveWSGIServer, _WSGIRequestHandler, _RedirectWSGIApp

        success_html = """<!DOCTYPE html><html><head><title>Authorization Successful</title><style>body{font-family:sans-serif;text-align:center;padding:50px;background:#0f172a;color:#f8fafc;}h1{color:#38bdf8;}p{color:#94a3b8;font-size:18px;}</style></head><body><h1>🎉 Authentication Successful!</h1><p>You may now close this window and return to your terminal.</p></body></html>"""
        wsgi_app = _RedirectWSGIApp(success_html)
        local_server = wsgiref.simple_server.make_server(
            "localhost",
            8080,
            wsgi_app,
            server_class=_ExclusiveWSGIServer,
            handler_class=_WSGIRequestHandler,
        )

        flow.redirect_uri = "http://localhost:8080/"
        auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

        prompt_msg = AuthUrlPrompt(BASE_DIR).format(url=auth_url)
        print(prompt_msg)
        sys.stdout.flush()

        local_server.timeout = 2
        start_time = time.time()
        max_wait = 7200  # 2 hours
        while time.time() - start_time < max_wait:
            local_server.handle_request()
            if wsgi_app.last_request_uri and ("code=" in wsgi_app.last_request_uri or "error=" in wsgi_app.last_request_uri):
                break

        local_server.server_close()

        if not wsgi_app.last_request_uri or "code=" not in wsgi_app.last_request_uri:
            raise TimeoutError("Timed out or cancelled waiting for Google login.")

        authorization_response = wsgi_app.last_request_uri.replace("http://", "https://")
        flow.fetch_token(authorization_response=authorization_response)
        creds = flow.credentials

        refresh_token = creds.refresh_token
        print("\n🎉 AUTHENTICATION SUCCESSFUL!\n")
        print("-" * 65)
        print(f"BLOGGER_CLIENT_ID={client_id}")
        print(f"BLOGGER_CLIENT_SECRET={client_secret}")
        print(f"BLOGGER_REFRESH_TOKEN={refresh_token}")

        detected_blog_id = ""
        # Try to find Blog ID automatically
        try:
            blogger_service = build("blogger", "v3", credentials=creds)
            blogs = blogger_service.blogs().listByUser(userId="self").execute()
            items = blogs.get("items", [])
            if items:
                print("\nDiscovered your Blogger blogs:")
                for blog in items:
                    print(f"👉 Blog Name: {blog.get('name')}")
                    print(f"   URL:       {blog.get('url')}")
                    print(f"   BLOG_ID:   {blog.get('id')}\n")
                    if "gpttype" in blog.get("url", "").lower() or not detected_blog_id:
                        detected_blog_id = blog.get("id")
            else:
                print("\nNo blogs found under this Google account.")
        except Exception as e:
            print(f"\nNote: Could not list blogs automatically ({e}).")

        # Automatically update .env file
        env_updates = {
            "BLOGGER_CLIENT_ID": client_id,
            "BLOGGER_CLIENT_SECRET": client_secret,
            "BLOGGER_REFRESH_TOKEN": refresh_token or ""
        }
        if detected_blog_id:
            env_updates["BLOG_ID"] = detected_blog_id

        update_env_file(env_updates)
        print("✅ Successfully updated your local .env file!")
        print("-" * 65)
        print("\nAll keys are ready!")

    except Exception as e:
        print(f"\n❌ Failed to authenticate: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
