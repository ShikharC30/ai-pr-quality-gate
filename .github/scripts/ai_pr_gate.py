import os
import subprocess
import requests
import json

def get_git_diff():
    try:
        subprocess.run(["git", "fetch", "origin", "main"], check=True)
        diff = subprocess.check_output(
            ["git", "diff", "origin/main...HEAD"], 
            text=True
        )
        return diff
    except Exception as e:
        print("Error fetching diff:", e)
        return ""

def get_event_flow_contract():
    contract_paths = ["event-flow.md", "src/event-flow.md", "docs/event-flow.md"]
    for path in contract_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    return "Standard idempotent, event-driven, and fault-tolerant architecture guidelines apply."

def main():
    diff_text = get_git_diff()
    if not diff_text.strip():
        print("No code changes found.")
        with open("pr_review.md", "w", encoding="utf-8") as f:
            f.write("✅ **No code changes detected.**")
        with open("verdict.json", "w", encoding="utf-8") as f:
            json.dump({"block_merge": False}, f)
        return

    diff_sample = diff_text[:8000]
    event_contract = get_event_flow_contract()

    system_instruction = (
        "You are an Automated Principal Architect and DevSecOps Lead conducting a dual-stage Pull Request review.\n\n"
        "### 📜 SERVICE EVENT FLOW & ARCHITECTURAL CONTRACT:\n"
        + event_contract + "\n\n"
        "### 💻 CODE DIFF:\n"
        + diff_sample + "\n\n"
        "Review the code diff and respond strictly using these EXACT markdown headings and format:\n\n"
        "## 🛠️ STAGE 1: GENERAL PR CODE REVIEW\n"
        "### ⚡ Summary of Code Changes\n"
        "- 2 to 3 concise bullet points summarizing what was added or changed.\n\n"
        "### 🛡️ Security, Vulnerabilities & Code Quality\n"
        "- Explicitly check for SQL injection, unsanitized inputs, unhandled exceptions, zero-division, and memory leaks.\n"
        "- State clearly if any critical vulnerability exists.\n\n"
        "## 🔄 STAGE 2: EVENT-FLOW & ARCHITECTURE COMPLIANCE\n"
        "### 📋 Contract Rules Verification\n"
        "- Line-by-line verification against the provided event-flow contract.\n"
        "- Highlight missing state transitions, missing event emissions, or violated idempotency keys.\n\n"
        "### ⚠️ Architecture Violations\n"
        "- State 'None' if compliant, otherwise describe the exact contract violation.\n\n"
        "## 🧪 STAGE 3: AUTOMATED UNIT TESTS (PROPOSED)\n"
        "Write complete, runnable PyTest test code inside a single ```python ... ``` code block.\n\n"
        "> 💡 **Action Item for Reviewer:**\n"
        "> If you like these generated tests, reply to this PR with the comment:\n"
        "> `bot apply-tests`\n"
        "> This will automatically commit them to this branch. Otherwise, simply ignore to skip.\n\n"
        "## 🚦 FINAL GATE VERDICT\n"
        "Write exactly either '[VERDICT: BLOCKED]' (if SQL injection, critical bug, or event contract violation is present) or '[VERDICT: APPROVED]'."
    )

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        with open("pr_review.md", "w", encoding="utf-8") as f:
            f.write("⚠️ **Error:** GEMINI_API_KEY missing.")
        return

    candidate_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-pro"]
    payload = {"contents": [{"parts": [{"text": system_instruction}]}]}

    review_body = None
    for model_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            res = requests.post(url, json=payload, timeout=50)
            res_data = res.json()
            if "candidates" in res_data and len(res_data["candidates"]) > 0:
                review_body = res_data["candidates"][0]["content"]["parts"][0]["text"]
                break
        except Exception:
            continue

    if not review_body:
        review_body = "⚠️ **Error:** Failed to generate review."

    # Parse verdict STRICTLY from the final verdict section (not inside generated test code)
    if "FINAL GATE VERDICT" in review_body:
        final_section = review_body.split("FINAL GATE VERDICT")[-1]
    else:
        final_section = review_body

    block_merge = "[VERDICT: BLOCKED]" in final_section

    with open("pr_review.md", "w", encoding="utf-8") as f:
        f.write(review_body)

    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump({"block_merge": block_merge}, f)

if __name__ == "__main__":
    main()
