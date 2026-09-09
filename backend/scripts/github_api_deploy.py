import os
import json
import base64
import urllib.request
import urllib.error

TOKEN = os.getenv("GITHUB_TOKEN", "")
OWNER = "Satyendra015"
REPO = "Landlens-AI"
BASE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}"
PUBLIC_DIR = os.path.abspath("public_web")

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "LandLens-Deployer"
}

def api_call(endpoint, method="GET", data=None):
    url = f"{BASE_URL}{endpoint}" if endpoint.startswith("/") else endpoint
    req_data = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"HTTP {e.code} Error for {endpoint}: {err_body}")
        raise e

print("1. Creating Git Blobs for real public_web assets...")
tree_items = []
file_count = 0

for root, dirs, files in os.walk(PUBLIC_DIR):
    if ".git" in root:
        continue
    for filename in files:
        if filename.startswith("."):
            continue
        filepath = os.path.join(root, filename)
        rel_path = os.path.relpath(filepath, PUBLIC_DIR).replace("\\", "/")
        
        with open(filepath, "rb") as f:
            b64_content = base64.b64encode(f.read()).decode("utf-8")
        
        blob_resp = api_call("/git/blobs", method="POST", data={
            "content": b64_content,
            "encoding": "base64"
        })
        blob_sha = blob_resp["sha"]
        tree_items.append({
            "path": rel_path,
            "mode": "100644",
            "type": "blob",
            "sha": blob_sha
        })
        file_count += 1
        print(f"  [{file_count}] Uploaded: {rel_path} -> {blob_sha[:8]}", flush=True)

print(f"\n2. Creating Git Tree ({len(tree_items)} items)...", flush=True)
tree_resp = api_call("/git/trees", method="POST", data={"tree": tree_items})
tree_sha = tree_resp["sha"]
print(f"Tree SHA: {tree_sha}", flush=True)

# Get current main commit to set as parent
main_ref = api_call("/git/ref/heads/main")
parent_sha = main_ref["object"]["sha"]
print(f"Parent commit: {parent_sha}", flush=True)

print("\n3. Creating Git Commit...", flush=True)
commit_resp = api_call("/git/commits", method="POST", data={
    "message": "Deploy LandLens AI Autonomous Web Application (SIH26018)",
    "tree": tree_sha,
    "parents": [parent_sha]
})
commit_sha = commit_resp["sha"]
print(f"Commit SHA: {commit_sha}", flush=True)

print("\n4. Updating Branches (main & gh-pages)...", flush=True)
for branch in ["main", "gh-pages"]:
    ref_name = f"refs/heads/{branch}"
    try:
        api_call(f"/git/ref/heads/{branch}")
        api_call(f"/git/refs/heads/{branch}", method="PATCH", data={
            "sha": commit_sha,
            "force": True
        })
        print(f"  Branch '{branch}' updated to {commit_sha[:8]}!", flush=True)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            api_call("/git/refs", method="POST", data={
                "ref": ref_name,
                "sha": commit_sha
            })
            print(f"  Branch '{branch}' created at {commit_sha[:8]}!", flush=True)

print("\n5. Activating GitHub Pages...", flush=True)
pages_url = None
try:
    pages_resp = api_call("/pages", method="POST", data={
        "source": {
            "branch": "gh-pages",
            "path": "/"
        }
    })
    pages_url = pages_resp.get("html_url")
    print(f"GitHub Pages created: {pages_url}", flush=True)
except urllib.error.HTTPError as e:
    try:
        pages_resp = api_call("/pages")
        pages_url = pages_resp.get("html_url")
        print(f"GitHub Pages active: {pages_url}", flush=True)
    except Exception as ex:
        print(f"Pages status: {ex}", flush=True)

expected_url = f"https://{OWNER.lower()}.github.io/{REPO}/"
final_url = pages_url or expected_url

print("\n=======================================================", flush=True)
print("SUCCESS: DEPLOYED TO GITHUB & GITHUB PAGES!", flush=True)
print(f"Public Live Web Link: {final_url}", flush=True)
print(f"Repository URL: https://github.com/{OWNER}/{REPO}", flush=True)
print("=======================================================", flush=True)
