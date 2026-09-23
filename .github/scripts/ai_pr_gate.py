import os
import subprocess
import requests

def get_git_diff():
    try:
        # Fetch target branch so git diff can compare
        subprocess.run(["git", "fetch", "origin", "main"], check=True)
        diff = subprocess.check_output(
            ["git", "diff", "origin/main...HEAD"], 
            text=True
        )
        return diff
    except Exception as e:
        print(f"Error fetching diff: {e}")
        return ""

def main():
    diff_text = get_git_diff()
    if not diff_text.strip():
        print("No code changes found in diff.")
        with open("pr_review.md", "w") as f:
            f.write("✅ **No code changes detected to review.**")
        return

    # Cap diff size to avoid hitting context limits
    diff_sample = diff_text[:12000]

    prompt = f"""
You are an Automated Principal Software Engineer & QA Architect reviewing a Pull Request.
Follow Cloudflare and Meta's code review guidelines.
Analyze the following git diff carefully:

```diff
{diff_sample}
