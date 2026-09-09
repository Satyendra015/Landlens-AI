import json
import base64
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.getenv("GITHUB_TOKEN", "")
OWNER = "Satyendra015"
REPO = "Landlens-AI"
BASE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"

files_to_update = [
    ("index.html", "public_web/index.html"),
    ("app.js", "public_web/app.js"),
    ("logo.png", "logo.png"),
    ("static/index.html", "public_web/static/index.html"),
    ("static/app.js", "public_web/static/app.js"),
    ("static/logo.png", "public_web/static/logo.png"),
    ("static/landlens_seal_exact.png", "public_web/static/landlens_seal_exact.png"),
    ("static/landlens_seal_circle.png", "public_web/static/landlens_seal_circle.png"),
    ("static/landlens_seal.png", "public_web/static/landlens_seal.png"),
    ("static/landlens_seal.jpg", "public_web/static/landlens_seal.jpg"),
    ("static/landlens_logo.png", "public_web/static/landlens_logo.png"),
    ("static/landlens_logo_full.png", "public_web/static/landlens_logo_full.png"),
    ("static/landlens_logo_icon.png", "public_web/static/landlens_logo_icon.png"),
    ("static/landlens_logo_transparent.png", "public_web/static/landlens_logo_transparent.png"),
    ("public_web/index.html", "public_web/index.html"),
    ("public_web/app.js", "public_web/app.js"),
    ("public_web/logo.png", "public_web/logo.png"),
    ("public_web/static/index.html", "public_web/static/index.html"),
    ("public_web/static/app.js", "public_web/static/app.js"),
    ("public_web/static/logo.png", "public_web/static/logo.png"),
    ("public_web/static/landlens_seal_exact.png", "public_web/static/landlens_seal_exact.png"),
    ("public_web/static/landlens_seal_circle.png", "public_web/static/landlens_seal_circle.png"),
    ("public_web/static/landlens_seal.png", "public_web/static/landlens_seal.png"),
    ("public_web/static/landlens_seal.jpg", "public_web/static/landlens_seal.jpg"),
    ("public_web/static/landlens_logo.png", "public_web/static/landlens_logo.png"),
    ("public_web/static/landlens_logo_full.png", "public_web/static/landlens_logo_full.png"),
    ("public_web/static/landlens_logo_icon.png", "public_web/static/landlens_logo_icon.png"),
    ("public_web/static/landlens_logo_transparent.png", "public_web/static/landlens_logo_transparent.png"),
    ("backend/app/static/index.html", "backend/app/static/index.html"),
    ("backend/app/static/app.js", "backend/app/static/app.js"),
    ("backend/app/static/landlens_seal_exact.png", "backend/app/static/landlens_seal_exact.png"),
    ("backend/app/static/landlens_seal_circle.png", "backend/app/static/landlens_seal_circle.png"),
    ("backend/app/static/landlens_seal.png", "backend/app/static/landlens_seal.png"),
    ("backend/app/static/landlens_seal.jpg", "backend/app/static/landlens_seal.jpg"),
    ("backend/app/static/landlens_logo.png", "backend/app/static/landlens_logo.png"),
    ("backend/app/static/landlens_logo_full.png", "backend/app/static/landlens_logo_full.png"),
    ("backend/app/static/landlens_logo_icon.png", "backend/app/static/landlens_logo_icon.png"),
    ("backend/app/static/landlens_logo_transparent.png", "backend/app/static/landlens_logo_transparent.png"),
    ("backend/scripts/process_new_logo.py", "backend/scripts/process_new_logo.py")
]

session = requests.Session()
session.headers.update({
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "FastSync"
})

def update_repo_file(remote_path, local_path, branch):
    if not os.path.exists(local_path):
        return f"Skipping {local_path} (not found)"
    try:
        with open(local_path, "rb") as f:
            b64_content = base64.b64encode(f.read()).decode("utf-8")
            
        sha = None
        url = f"{BASE_URL}/{remote_path}?ref={branch}"
        r = session.get(url, timeout=10)
        if r.status_code == 200:
            sha = r.json().get("sha")

        put_data = {
            "message": f"Fix emblem badge cutoff: unclipped pure seal with antialiasing ({remote_path})",
            "content": b64_content,
            "branch": branch
        }
        if sha:
            put_data["sha"] = sha

        put_r = session.put(f"{BASE_URL}/{remote_path}", json=put_data, timeout=15)
        if put_r.status_code in [200, 201]:
            commit_sha = put_r.json().get("commit", {}).get("sha", "ok")[:8]
            return f"Updated {remote_path} on {branch}! Commit: {commit_sha}"
        else:
            return f"Error {put_r.status_code} on {remote_path} ({branch}): {put_r.text[:100]}"
    except Exception as e:
        return f"Exception on {remote_path} ({branch}): {e}"

print("Uploading clean LandLens AI logo & emblem assets to GitHub...")
tasks = []
with ThreadPoolExecutor(max_workers=5) as executor:
    for branch in ["gh-pages", "main"]:
        for remote_p, local_p in files_to_update:
            tasks.append(executor.submit(update_repo_file, remote_p, local_p, branch))

    for future in as_completed(tasks):
        res = future.result()
        print(res)

print("\nAll logo updates deployed successfully!")

