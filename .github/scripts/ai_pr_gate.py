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
        "You are an Automated Principal Architect and DevSecOps Gatekeeper reviewing a Pull Request.\n\n"
        "### 📜 SERVICE EVENT FLOW & ARCHITECTURAL CONTRACT:\n"
        + event_contract + "\n\n"
        "### 💻 CODE DIFF:\n"
        + diff_sample + "\n\n"
        "Review the diff thoroughly and respond strictly using these EXACT markdown headings:\n\n"
        "## 🛠️ STAGE 1: GENERAL PR CODE REVIEW\n"
        "### ⚡ Summary of Code Changes\n"
        "- 2 to 3 concise bullet points summarizing what was added or changed.\n\n"
        "### 🛡️ Security, Vulnerabilities & Code Quality\n"
        "- Flag any SQL injection, unsanitized input, zero division, missing error handling, or code smell.\n"
        "- State 'No issues found' ONLY if the code is 100% production perfect.\n\n"
        "## 🔄 STAGE 2: EVENT-FLOW & ARCHITECTURE COMPLIANCE\n"
        "### 📋 Contract Rules Verification\n"
        "- Verify compliance against event-flow.md rules (e.g. idempotency, event emission, query standards).\n\n"
        "### ⚠️ Architecture Violations\n"
        "- State 'None' or describe the contract violations.\n\n"
        "## 🧪 STAGE 3: AUTOMATED UNIT TESTS (PROPOSED)\n"
        "Write complete, runnable PyTest test code inside a single ```python ... ``` code block.\n\n"
        "## 🚦 FINAL GATE VERDICT\n"
        "STRICT POLICY: If there are ANY security issues, bugs, code quality comments, or contract violations, write exactly: [VERDICT: BLOCKED]\n"
        "Write [VERDICT: APPROVED] ONLY if there are zero issues, zero warnings, and zero contract violations."
    )

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        with open("pr_review.md", "w", encoding="utf-8") as f:
            f.write("⚠️ **Error:** GEMINI_API_KEY missing from environment secrets.")
        with open("verdict.json", "w", encoding="utf-8") as f:
            json.dump({"block_merge": True}, f)
        return

    candidate_models = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-flash-latest"]
    payload = {"contents": [{"parts": [{"text": system_instruction}]}]}

    review_body = None
    debug_errors = []

    for model_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            res = requests.post(url, json=payload, timeout=60)
            res_data = res.json()
            if "candidates" in res_data and len(res_data["candidates"]) > 0:
                review_body = res_data["candidates"][0]["content"]["parts"][0]["text"]
                break
            elif "error" in res_data:
                debug_errors.append(f"{model_name}: {res_data['error'].get('message')}")
        except Exception as e:
            debug_errors.append(f"{model_name}: {str(e)}")

    if not review_body:
        review_body = f"⚠️ **Error: Failed to generate review.**\n\n`Debug Info: {' | '.join(debug_errors)}`"

    # Strictly check the final verdict section
    if "FINAL GATE VERDICT" in review_body:
        final_section = review_body.split("FINAL GATE VERDICT")[-1]
    else:
        final_section = review_body

    block_merge = "[VERDICT: BLOCKED]" in final_section

    action_items_box = (
        "\n\n---\n"
        "### 💡 Reviewer Actions\n"
        "- **Apply Unit Tests:** Reply `bot apply-tests` to automatically commit the suggested tests to this branch.\n"
        "- **Ignore Comments & Unblock Merge:** Reply `bot ignore-and-pass` to bypass this check if you accept the changes."
    )

    full_markdown_output = review_body + action_items_box

    with open("pr_review.md", "w", encoding="utf-8") as f:
        f.write(full_markdown_output)

    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump({"block_merge": block_merge}, f)

if __name__ == "__main__":
    main()
