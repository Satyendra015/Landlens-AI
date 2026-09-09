import subprocess
import os

cwd = os.path.abspath("public_web")
token = os.getenv("GITHUB_TOKEN", "")
token_url = f"https://{token}@github.com/Satyendra015/Landlens-AI.git" if token else "https://github.com/Satyendra015/Landlens-AI.git"

# Configure git
subprocess.run("git config http.postBuffer 524288000", cwd=cwd, shell=True)
subprocess.run("git config http.version HTTP/1.1", cwd=cwd, shell=True)

# Remove large sample images for initial push so it is ~550KB
subprocess.run("git rm -r --cached sample-data", cwd=cwd, shell=True, capture_output=True)
subprocess.run("git commit -m \"Deploy core LandLens AI web application\"", cwd=cwd, shell=True, capture_output=True)

print("Pushing core 550KB application to gh-pages...")
p = subprocess.run(f"git push -f {token_url} gh-pages", cwd=cwd, shell=True, capture_output=True, text=True)
print(f"Exit code: {p.returncode}")
if p.stdout.strip():
    print(f"STDOUT: {p.stdout.strip()}")
if p.stderr.strip():
    print(f"STDERR: {p.stderr.strip()}")

if p.returncode == 0:
    print("\nSUCCESS: Core application pushed to GitHub!")
