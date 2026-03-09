import json
import httpx
from langchain_core.tools import tool
from services.github import parse_pr_url, github_headers

@tool
def fetch_pr_metadata(pr_url: str) -> str:
    """
    Fetch Pull Request metadata from GitHub:
    title, author, state, base/head branches, file count,
    additions, deletions, labels, and milestone.
    
    Input: Full GitHub PR URL e.g. https://github.com/owner/repo/pull/123
    """
    # ── Input validation ──
    if not pr_url or not pr_url.strip():
        return "ERROR: pr_url cannot be empty."

    parsed = parse_pr_url(pr_url.strip())
    if not parsed:
        return (
            "ERROR: Invalid GitHub PR URL format. "
            "Expected: https://github.com/owner/repo/pull/123"
        )

    owner, repo, pr_number = parsed

    try:
        # ── Fetch PR metadata from GitHub API ──
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"

        with httpx.Client(timeout=15.0) as client:
            response = client.get(api_url, headers=github_headers())

        if response.status_code == 404:
            return f"ERROR: PR #{pr_number} not found in {owner}/{repo}. Check the URL or ensure the repo is public."

        if response.status_code == 403:
            return "ERROR: GitHub API rate limit exceeded or token lacks permissions. Try again in a minute."

        if response.status_code == 401:
            return "ERROR: GitHub token is invalid or expired. Check your GITHUB_TOKEN env variable."

        response.raise_for_status()
        pr = response.json()

        # ── Also fetch changed files list ──
        files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
        files_response = client.get(files_url, headers=github_headers())
        files_data = files_response.json() if files_response.status_code == 200 else []

        # Extract file names and their change types
        changed_files = []
        for f in files_data[:20]:  # cap at 20 files to avoid token overflow
            changed_files.append({
                "filename": f.get("filename"),
                "status": f.get("status"),       # added, modified, removed, renamed
                "additions": f.get("additions", 0),
                "deletions": f.get("deletions", 0),
            })

        # ── Build structured metadata ──
        labels = [label["name"] for label in pr.get("labels", [])]
        reviewers = [r["login"] for r in pr.get("requested_reviewers", [])]

        metadata = {
            "pr_number": pr_number,
            "title": pr.get("title", "Unknown"),
            "author": pr.get("user", {}).get("login", "Unknown"),
            "state": pr.get("state", "unknown"),
            "draft": pr.get("draft", False),
            "base_branch": pr.get("base", {}).get("ref", "unknown"),
            "head_branch": pr.get("head", {}).get("ref", "unknown"),
            "created_at": pr.get("created_at", ""),
            "updated_at": pr.get("updated_at", ""),
            "additions": pr.get("additions", 0),
            "deletions": pr.get("deletions", 0),
            "changed_files_count": pr.get("changed_files", 0),
            "commits": pr.get("commits", 0),
            "labels": labels,
            "requested_reviewers": reviewers,
            "milestone": pr.get("milestone", {}).get("title") if pr.get("milestone") else None,
            "body": (pr.get("body") or "No description provided.")[:500],  # cap length
            "changed_files": changed_files,
        }

        return json.dumps(metadata, indent=2)

    except httpx.TimeoutException:
        return f"ERROR: GitHub API timed out fetching PR #{pr_number}. Try again."
    except httpx.RequestError as e:
        return f"ERROR: Network error fetching PR metadata — {str(e)}"
    except Exception as e:
        return f"ERROR: Unexpected failure in fetch_pr_metadata — {type(e).__name__}: {str(e)}"


@tool
def fetch_pr_diff(pr_url: str) -> str:
    """
    Fetch the actual code diff for a Pull Request.
    Returns the raw diff showing exactly what lines were added/removed.
    
    Input: Full GitHub PR URL e.g. https://github.com/owner/repo/pull/123
    """
    if not pr_url or not pr_url.strip():
        return "ERROR: pr_url cannot be empty."

    parsed = parse_pr_url(pr_url.strip())
    if not parsed:
        return "ERROR: Invalid GitHub PR URL format."

    owner, repo, pr_number = parsed

    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"

        # GitHub returns diff when you request with Accept: application/vnd.github.diff
        diff_headers = {**github_headers(), "Accept": "application/vnd.github.diff"}

        with httpx.Client(timeout=20.0) as client:
            response = client.get(api_url, headers=diff_headers)

        if response.status_code == 404:
            return f"ERROR: PR #{pr_number} not found in {owner}/{repo}."
        if response.status_code == 403:
            return "ERROR: GitHub API rate limit exceeded."

        response.raise_for_status()

        diff_text = response.text

        if not diff_text.strip():
            return "No diff available — this PR may have no file changes."

        # ── Cap diff size to avoid overflowing the LLM context window ──
        # A massive diff (10k lines) would use too many tokens and degrade reasoning.
        # We take the first 4000 chars which covers most meaningful PRs.
        MAX_DIFF_CHARS = 4000
        if len(diff_text) > MAX_DIFF_CHARS:
            diff_text = diff_text[:MAX_DIFF_CHARS] + (
                f"\n\n... [DIFF TRUNCATED — showing first {MAX_DIFF_CHARS} chars of "
                f"{len(response.text)} total chars. Analyze based on what's visible.] ..."
            )

        return diff_text

    except httpx.TimeoutException:
        return f"ERROR: Timed out fetching diff for PR #{pr_number}."
    except httpx.RequestError as e:
        return f"ERROR: Network error fetching diff — {str(e)}"
    except Exception as e:
        return f"ERROR: Unexpected failure in fetch_pr_diff — {type(e).__name__}: {str(e)}"


@tool
def assess_risk(metadata_json: str, diff_snippet: str) -> str:
    """
    Assess the risk level of a PR based on its metadata and diff.
    Returns a structured risk assessment with score, level, and reasons.
    
    Inputs:
        metadata_json: JSON string from fetch_pr_metadata
        diff_snippet: diff text from fetch_pr_diff
    """
    if not metadata_json:
        return "ERROR: metadata_json is required for risk assessment."

    try:
        metadata = json.loads(metadata_json)
    except json.JSONDecodeError:
        return "ERROR: metadata_json is not valid JSON. Pass the direct output of fetch_pr_metadata."

    risk_score = 0
    risk_reasons = []
    risk_positives = []

    # ── Rule 1: Size of changes ──
    additions = metadata.get("additions", 0)
    deletions = metadata.get("deletions", 0)
    total_changes = additions + deletions

    if total_changes > 500:
        risk_score += 3
        risk_reasons.append(f"Large PR: {total_changes} total line changes (>500 is high risk)")
    elif total_changes > 200:
        risk_score += 2
        risk_reasons.append(f"Medium-sized PR: {total_changes} line changes")
    elif total_changes > 50:
        risk_score += 1
    else:
        risk_positives.append(f"Small, focused PR: only {total_changes} line changes")

    # ── Rule 2: Number of files changed ──
    files_changed = metadata.get("changed_files_count", 0)
    if files_changed > 20:
        risk_score += 3
        risk_reasons.append(f"Touches many files: {files_changed} files (hard to review thoroughly)")
    elif files_changed > 10:
        risk_score += 2
        risk_reasons.append(f"Touches {files_changed} files")
    else:
        risk_positives.append(f"Focused scope: {files_changed} files changed")

    # ── Rule 3: Sensitive file patterns in diff ──
    sensitive_patterns = {
        "auth": "Authentication/authorization logic changed",
        "password": "Password handling code changed",
        "secret": "Potential secret/key handling",
        "token": "Token handling code changed",
        "migration": "Database migration detected",
        "schema": "Schema changes detected",
        "config": "Configuration file changed",
        "env": "Environment configuration changed",
        "dockerfile": "Docker configuration changed",
        ".github/workflows": "CI/CD pipeline changed",
        "requirements": "Dependency changes detected",
        "package.json": "Node.js dependencies changed",
    }

    diff_lower = diff_snippet.lower() if diff_snippet else ""
    metadata_str = json.dumps(metadata).lower()

    for pattern, reason in sensitive_patterns.items():
        if pattern in diff_lower or pattern in metadata_str:
            risk_score += 2
            risk_reasons.append(f"⚠️  {reason}")

    # ── Rule 4: Draft PR ──
    if metadata.get("draft"):
        risk_score += 1
        risk_reasons.append("This is a DRAFT PR — may not be ready for merge")

    # ── Rule 5: No reviewers assigned ──
    if not metadata.get("requested_reviewers"):
        risk_score += 1
        risk_reasons.append("No reviewers assigned")
    else:
        risk_positives.append(f"Has {len(metadata['requested_reviewers'])} reviewer(s) assigned")

    # ── Rule 6: No description ──
    body = metadata.get("body", "")
    if not body or body == "No description provided." or len(body) < 30:
        risk_score += 1
        risk_reasons.append("Missing or very short PR description")
    else:
        risk_positives.append("Has a PR description")

    # ── Dangerous diff patterns ──
    danger_patterns = [
        ("eval(", "Uses eval() — potential code injection risk"),
        ("exec(", "Uses exec() — potential code injection risk"),
        ("DROP TABLE", "SQL DROP TABLE statement detected"),
        ("DELETE FROM", "SQL DELETE statement detected"),
        ("force_push", "Force push reference detected"),
        ("rm -rf", "Destructive shell command detected"),
        ("chmod 777", "Insecure file permissions detected"),
        ("TODO: fix", "Has unresolved TODOs marked for fixing"),
        ("FIXME", "Has FIXME markers in code"),
        ("hardcoded", "Hardcoded values detected"),
    ]

    for pattern, reason in danger_patterns:
        if pattern.lower() in diff_lower:
            risk_score += 3
            risk_reasons.append(f"🚨 DANGER: {reason}")

    # ── Compute final risk level ──
    if risk_score >= 10:
        risk_level = "CRITICAL"
        merge_recommendation = "DO NOT MERGE without thorough review by senior engineer"
    elif risk_score >= 7:
        risk_level = "HIGH"
        merge_recommendation = "Requires careful review — multiple risk factors present"
    elif risk_score >= 4:
        risk_level = "MEDIUM"
        merge_recommendation = "Review recommended before merging"
    elif risk_score >= 2:
        risk_level = "LOW"
        merge_recommendation = "Looks reasonable — standard review sufficient"
    else:
        risk_level = "MINIMAL"
        merge_recommendation = "Low-risk change — can merge after quick review"

    result = {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "merge_recommendation": merge_recommendation,
        "risk_factors": risk_reasons if risk_reasons else ["No significant risk factors found"],
        "positive_signals": risk_positives if risk_positives else [],
    }

    return json.dumps(result, indent=2)

tools = [fetch_pr_metadata, fetch_pr_diff, assess_risk]
tools_by_name = {t.name: t for t in tools}
