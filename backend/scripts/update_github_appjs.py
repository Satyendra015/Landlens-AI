import json
import base64
import urllib.request
import urllib.error

TOKEN = os.getenv("GITHUB_TOKEN", "")
OWNER = "Satyendra015"
REPO = "Landlens-AI"
BASE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"

with open("public_web/static/app.js", "rb") as f:
    app_js_b64 = base64.b64encode(f.read()).decode("utf-8")

with open("public_web/index.html", "rb") as f:
    index_html_b64 = base64.b64encode(f.read()).decode("utf-8")

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "LandLens-Updater"
}

def update_file(path, branch, content_b64, msg):
    url = f"{BASE_URL}/{path}?ref={branch}"
    req = urllib.request.Request(url, headers=headers)
    sha = None
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            sha = data.get("sha")
    except Exception as e:
        print(f"File {path} on {branch} not found or error: {e}")

    put_data = {
        "message": msg,
        "content": content_b64,
        "branch": branch
    }
    if sha:
        put_data["sha"] = sha

    put_req = urllib.request.Request(
        f"{BASE_URL}/{path}",
        data=json.dumps(put_data).encode("utf-8"),
        headers=headers,
        method="PUT"
    )
    with urllib.request.urlopen(put_req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print(f"Updated {path} on branch {branch}! New commit: {res['commit']['sha'][:8]}")

files_to_sync = [
    ("app.js", app_js_b64, "Fix Verification Studio, Cadastral GIS, and Land Records Interactivity"),
    ("static/app.js", app_js_b64, "Fix Verification Studio, Cadastral GIS, and Land Records Interactivity"),
    ("index.html", index_html_b64, "Add GIS button and update layout for cross-module integration"),
    ("static/index.html", index_html_b64, "Add GIS button and update layout for cross-module integration")
]

for branch in ["gh-pages", "main"]:
    print(f"\n--- Syncing branch: {branch} ---")
    for path, b64_c, msg in files_to_sync:
        try:
            update_file(path, branch, b64_c, msg)
        except Exception as e:
            print(f"Error updating {path} on {branch}: {e}")

print("\nAll GitHub Pages and Main branch assets updated successfully!")

