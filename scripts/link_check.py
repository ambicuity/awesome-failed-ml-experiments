#!/usr/bin/env python3
"""
Link Checker for Awesome Failed ML Experiments

This script validates all links in submission files to ensure:
- No dead links (404s, timeouts, etc.)
- Links are accessible
- Proper URL format

Author: Ritesh Rana (riteshrana36@gmail.com)
"""

import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import requests

# =============================================================================
# CONFIGURATION
# =============================================================================

# Request timeout in seconds
REQUEST_TIMEOUT = 10

# Maximum number of concurrent requests
MAX_WORKERS = 5

# User agent to use for requests (some sites block default Python agent)
USER_AGENT = (
    "Mozilla/5.0 (compatible; AwesomeFailedMLBot/1.0; "
    "+https://github.com/ambicuity/awesome-failed-ml-experiments)"
)

# HTTP status codes considered successful
SUCCESS_CODES = range(200, 400)

# URLs to skip validation (known problematic domains or internal links)
SKIP_PATTERNS = [
    r"^mailto:",
    r"^tel:",
    r"^#",  # Internal anchors
    r"localhost",
    r"127\.0\.0\.1",
    r"example\.com",
]

# Domains that often block automated requests (warn but don't fail)
WARN_DOMAINS = [
    "twitter.com",
    "x.com",
    "linkedin.com",
    "facebook.com",
    "instagram.com",
    "arxiv.org",  # Often has rate limiting
    "github.com",  # May require auth for some resources
]

# Domains that are known reliable but may be blocked in CI environments
# These are treated as valid without checking
TRUSTED_DOMAINS = [
    "arxiv.org",
    "doi.org",
    "dl.acm.org",
    "papers.nips.cc",
    "openreview.net",
    "aclanthology.org",
]

# =============================================================================
# LINK EXTRACTION
# =============================================================================


def extract_links(content: str) -> list[str]:
    """
    Extract all URLs from markdown content.

    Matches:
    - Markdown links: [text](url)
    - Raw URLs: https://... or http://...

    Args:
        content: The markdown content to search

    Returns:
        List of unique URLs found
    """
    links = set()

    # Pattern for markdown links: [text](url)
    markdown_pattern = r"\[([^\]]*)\]\(([^)]+)\)"
    for match in re.finditer(markdown_pattern, content):
        url = match.group(2).strip()
        links.add(url)

    # Pattern for raw URLs
    url_pattern = r"https?://[^\s\)\]\"'<>]+"
    for match in re.finditer(url_pattern, content):
        url = match.group(0).strip()
        # Clean up trailing punctuation
        url = re.sub(r"[.,;:!?]+$", "", url)
        links.add(url)

    return list(links)


def should_skip_url(url: str) -> bool:
    """
    Check if a URL should be skipped from validation.

    Args:
        url: The URL to check

    Returns:
        True if the URL should be skipped
    """
    return any(re.search(pattern, url, re.IGNORECASE) for pattern in SKIP_PATTERNS)


def is_warn_domain(url: str) -> bool:
    """
    Check if a URL is from a domain that often blocks bots.

    Args:
        url: The URL to check

    Returns:
        True if the domain is known to block automated requests
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        for warn_domain in WARN_DOMAINS:
            if warn_domain in domain:
                return True
    except Exception:
        pass
    return False


def is_trusted_domain(url: str) -> bool:
    """
    Check if a URL is from a known trusted domain.

    These domains are assumed valid without network checks to handle
    CI environments with network restrictions.

    Args:
        url: The URL to check

    Returns:
        True if the domain is trusted
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        for trusted in TRUSTED_DOMAINS:
            if trusted in domain:
                return True
    except Exception:
        pass
    return False


# =============================================================================
# LINK VALIDATION
# =============================================================================


def check_link(url: str) -> tuple[str, bool, str]:
    """
    Check if a single URL is accessible.

    Args:
        url: The URL to check

    Returns:
        Tuple of (url, is_valid, message)
    """
    # Skip certain URLs
    if should_skip_url(url):
        return (url, True, "Skipped (internal/special link)")

    # Validate URL format
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return (url, False, "Invalid URL format")
    except Exception as e:
        return (url, False, f"URL parsing error: {e}")

    # Check if it's a trusted domain (assume valid without checking)
    if is_trusted_domain(url):
        return (url, True, "OK (trusted domain)")

    # Check if it's a warn domain (don't fail, just warn)
    if is_warn_domain(url):
        return (url, True, "Warning: Domain may block automated requests")

    # Make the request
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.head(
            url,
            timeout=REQUEST_TIMEOUT,
            headers=headers,
            allow_redirects=True,
        )

        # Some servers don't support HEAD, try GET
        if response.status_code == 405:
            response = requests.get(
                url,
                timeout=REQUEST_TIMEOUT,
                headers=headers,
                allow_redirects=True,
                stream=True,  # Don't download the whole response
            )
            # Close the connection immediately
            response.close()

        if response.status_code in SUCCESS_CODES:
            return (url, True, f"OK ({response.status_code})")
        else:
            return (url, False, f"HTTP {response.status_code}")

    except requests.exceptions.Timeout:
        return (url, False, "Timeout")
    except requests.exceptions.ConnectionError:
        return (url, False, "Connection error")
    except requests.exceptions.TooManyRedirects:
        return (url, False, "Too many redirects")
    except requests.exceptions.RequestException as e:
        return (url, False, f"Request error: {e}")
    except Exception as e:
        return (url, False, f"Unexpected error: {e}")


def check_links_parallel(urls: list[str]) -> list[tuple[str, bool, str]]:
    """
    Check multiple URLs in parallel.

    Args:
        urls: List of URLs to check

    Returns:
        List of (url, is_valid, message) tuples
    """
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_url = {executor.submit(check_link, url): url for url in urls}

        # Collect results as they complete
        for future in as_completed(future_to_url):
            result = future.result()
            results.append(result)

    return results


# =============================================================================
# FILE PROCESSING
# =============================================================================


def check_file_links(filepath: Path) -> tuple[bool, list[tuple[str, bool, str]]]:
    """
    Check all links in a single file.

    Args:
        filepath: Path to the file to check

    Returns:
        Tuple of (all_valid, list of (url, is_valid, message) results)
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return (False, [("", False, f"Failed to read file: {e}")])

    # Extract links
    links = extract_links(content)

    if not links:
        return (True, [])

    # Check all links
    results = check_links_parallel(links)

    # Determine if all passed
    all_valid = all(is_valid for _, is_valid, _ in results)

    return (all_valid, results)


def find_markdown_files(base_path: Path) -> list[Path]:
    """
    Find all markdown files in the submissions directory.

    Args:
        base_path: Path to the repository root

    Returns:
        List of paths to markdown files
    """
    submissions_dir = base_path / "submissions"
    if not submissions_dir.exists():
        return []

    return list(submissions_dir.glob("**/*.md"))


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


def main() -> int:
    """
    Main entry point for the link checker script.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Determine repository root
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent

    # Get files to check from command line args or find all
    if len(sys.argv) > 1:
        files_to_check = [Path(arg) for arg in sys.argv[1:]]
    else:
        files_to_check = find_markdown_files(repo_root)

    if not files_to_check:
        print("✅ No files to check for links.")
        return 0

    print(f"🔗 Checking links in {len(files_to_check)} file(s)...\n")

    all_valid = True
    total_links = 0
    broken_links = 0

    for filepath in files_to_check:
        print(f"📄 Checking: {filepath.name}")

        is_valid, results = check_file_links(filepath)

        if not results:
            print("   No links found\n")
            continue

        total_links += len(results)

        if is_valid:
            print(f"   ✅ All {len(results)} link(s) valid\n")
        else:
            all_valid = False
            for url, valid, message in results:
                if not valid:
                    broken_links += 1
                    print(f"   ❌ {url}")
                    print(f"      Error: {message}")
            print()

    # Print summary
    print("=" * 60)
    print(f"📊 Summary: {total_links} link(s) checked, {broken_links} broken")
    print()

    if all_valid:
        print("✅ All links are valid!")
        return 0
    else:
        print("❌ Some links are broken. Please fix them and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
