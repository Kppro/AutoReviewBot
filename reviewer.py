#!/usr/bin/env python3

"""
Usage Examples:

1) Standalone to review unstaged changes:
   ./reviewer

2) From pre-commit hook (staged changes):
   - In .git/hooks/pre-commit, add something like:
       #!/bin/bash
       reviewer --pre-commit
       exit_code=$?
       if [ $exit_code -ne 0 ]; then
         echo "Aborting commit..."
         exit 1
       fi
       exit 0

3) Review a GitHub pull request by URL:
   ./reviewer --url https://github.com/<org>/<repo>/pull/<pr_number>
"""

import os
import sys
import subprocess
import argparse
from openai import OpenAI
import requests

# =========================================
# List of extensions to exclude
# =========================================
EXCLUDED_EXTENSIONS = [
    ".pbxproj",
    ".storyboard",
    ".svg",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    # Add or remove extensions as needed
]

def get_local_diff(only_staged: bool) -> str:
    """
    Return the git diff as a string.
    If only_staged=True, uses 'git diff --staged' (for pre-commit).
    Otherwise, uses 'git diff' (unstaged changes).
    """
    cmd = ["git", "diff"]
    if only_staged:
        cmd.append("--staged")
    try:
        diff_output = subprocess.check_output(cmd, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {' '.join(cmd)}: {e}", file=sys.stderr)
        return ""
    return diff_output

def get_github_pr_diff(url: str) -> str:
    # Expect a URL like: https://github.com/<org>/<repo>/pull/<pr_number>
    # Convert it to:     https://api.github.com/repos/<org>/<repo>/pulls/<pr_number>
    
    # 1. Extract owner/repo/pull_number from the original URL
    #    Example: org = "MyOrg", repo = "my-repo", pr = "12"
    #    Then build the API URL: https://api.github.com/repos/MyOrg/my-repo/pulls/12
    
    import re
    
    match = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", url)
    if not match:
        print(f"Invalid PR URL: {url}")
        return ""
    
    owner, repo, pr = match.groups()
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr}"

    headers = {
        "Accept": "application/vnd.github.v3.diff"  # Request diff format
    }
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    try:
        resp = requests.get(api_url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Error fetching PR diff from {api_url}: {e}")
        return ""


def filter_excluded_files(diff: str, excluded_exts) -> str:
    """
    Parses the diff in chunks. If a chunk involves a file with an excluded
    extension, that chunk is omitted entirely.
    """
    if not diff.strip():
        return diff

    lines = diff.splitlines(keepends=False)
    kept_chunks = []
    current_chunk_lines = []
    skip_current_chunk = False

    diff_header_prefix = "diff --git "

    def finalize_chunk():
        """Helper to finalize a chunk if we're not skipping it."""
        if not skip_current_chunk and current_chunk_lines:
            kept_chunks.extend(current_chunk_lines)

    for line in lines:
        if line.startswith(diff_header_prefix):
            # finalize the current chunk
            finalize_chunk()
            current_chunk_lines = []
            skip_current_chunk = False

            # The line looks like: "diff --git a/path b/path"
            parts = line.split()
            if len(parts) >= 4:
                file_a = parts[2][2:]  # remove the 'a/' prefix
                file_b = parts[3][2:]  # remove the 'b/' prefix

                # Check if extension is in the excluded list
                for ext in excluded_exts:
                    if file_a.endswith(ext) or file_b.endswith(ext):
                        skip_current_chunk = True
                        break

            # start the new chunk lines with the diff header line (even if skipping)
            current_chunk_lines = [line]
        else:
            # normal line within the chunk
            current_chunk_lines.append(line)

    # finalize the last chunk
    finalize_chunk()

    # reassemble
    return "\n".join(kept_chunks) + "\n"


def call_openai_api(diff_content: str, context: str) -> str:
    """
    Analyze `diff_content` with OpenAI and return suggestions.
    `context` is a short descriptor like "Staged changes" or a PR URL.
    """
    if not diff_content.strip():
        return "No diff content provided."

    # Instantiate the client
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),  # Or just rely on OPENAI_API_KEY in env
    )

    # Prepare prompts
    system_prompt = (
        "You are an AI code reviewer. You will receive a Git diff "
        "and should provide feedback on potential issues, typos, improvements, "
        "keep it short by focusing on potential errors that could cause production issues. "
        "if nothing major is preventing the diff to be commit, then just reply with only one word: 'APPROVED'."
    )
    user_prompt = (
        f"Context: {context}\n"
        f"Here is the diff:\n\n"
        f"{diff_content}\n\n"
        "Please provide your review with suggestions."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Adjust to your desired model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=2000,
            temperature=0.5,
        )
        # Retrieve text from the first choice
        ai_message = response.choices[0].message.content.strip()
        return ai_message
    except Exception as e:
        return f"Error calling OpenAI API: {e}"


def main():
    parser = argparse.ArgumentParser(
        description="Analyze code changes using OpenAI."
    )
    parser.add_argument(
        "--pre-commit",
        action="store_true",
        help="Analyze staged changes (useful for pre-commit hook)."
    )
    parser.add_argument(
        "--url",
        type=str,
        help="GitHub pull request URL (e.g. https://github.com/org/repo/pull/123)"
    )

    args = parser.parse_args()

    if args.url:
        # 1. Fetch PR diff
        diff_content = get_github_pr_diff(args.url)
        context = f"GitHub PR URL: {args.url}"
    elif args.pre_commit:
        # 2. Get staged diff
        diff_content = get_local_diff(only_staged=True)
        context = "Staged changes (pre-commit)"
    else:
        # 3. Get unstaged diff
        diff_content = get_local_diff(only_staged=False)
        context = "Unstaged changes (local working directory)"

    # =========================================
    # Filter out unwanted file types
    # =========================================
    diff_content = filter_excluded_files(diff_content, EXCLUDED_EXTENSIONS)

    if not diff_content.strip():
        print("No diff found (after filtering). Exiting.")
        sys.exit(0)

    print("Analyzing with OpenAI, please wait...")
    feedback = call_openai_api(diff_content, context)

    print("\n----- AI REVIEW START -----")
    print(feedback)
    print("----- AI REVIEW END -----\n")

    # Automatically detect APPROVED and proceed or abort
    if "APPROVED" in feedback:
        print("AI review result: APPROVED. Proceeding with the commit.")
        sys.exit(0)  # Exit with success
    else:
        print("AI review result: Not approved. Aborting the commit.")
        sys.exit(1)  # Exit with failure



if __name__ == "__main__":
    main()
