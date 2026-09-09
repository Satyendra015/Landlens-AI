import subprocess
import os
import sys

token = os.getenv("GITHUB_TOKEN", "")
token_url = f"https://{token}@github.com/Satyendra015/Landlens-AI.git" if token else "https://github.com/Satyendra015/Landlens-AI.git"
cwd = os.path.abspath("public_web")

def run(cmd):
    print(f"Executing: {cmd}")
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if res.stdout.strip():
        print(f"STDOUT: {res.stdout.strip()}")
    if res.stderr.strip():
        print(f"STDERR: {res.stderr.strip()}")
    return res.returncode

run("git init")
run('git config user.name "Satyendra015"')
run('git config user.email "sniperonaction00008@gmail.com"')
run("git config http.postBuffer 524288000")
run("git checkout -b gh-pages")
run("git add .")
run('git commit -m "Deploy LandLens AI Web App to GitHub Pages"')
code = run(f"git push -f {token_url} gh-pages")

if code == 0:
    print("\n=======================================================")
    print("SUCCESS: Deployed to gh-pages branch on GitHub!")
    print("GitHub Pages URL: https://satyendra015.github.io/Landlens-AI/")
    print("=======================================================")
else:
    print(f"\nFailed to push with exit code {code}")
