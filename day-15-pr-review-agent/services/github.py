import re
from config import GITHUB_TOKEN

def parse_pr_url(url: str) -> tuple[str, str, int] | None:
    """
    Parse a GitHub PR URL into (owner, repo, pr_number).
    Handles formats:
      https://github.com/owner/repo/pull/123
      https://github.com/owner/repo/pull/123/files
    """
    pattern = r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.search(pattern, url)
    if not match:
        return None
    return match.group(1), match.group(2), int(match.group(3))


def github_headers() -> dict:
    """Standard GitHub API headers."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers
