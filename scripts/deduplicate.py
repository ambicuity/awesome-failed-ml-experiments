#!/usr/bin/env python3
"""
Duplicate Detection for Awesome Failed ML Experiments

This script detects duplicate or highly similar submissions using:
- Title similarity (fuzzy matching)
- Content similarity (using difflib SequenceMatcher)
- Hash-based exact matching

Author: Ritesh Rana (riteshrana36@gmail.com)
"""

import hashlib
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

import frontmatter

# =============================================================================
# CONFIGURATION
# =============================================================================

# Similarity threshold (0.0 to 1.0)
# Submissions with similarity above this are flagged as potential duplicates
TITLE_SIMILARITY_THRESHOLD = 0.8
CONTENT_SIMILARITY_THRESHOLD = 0.6

# Minimum content length to consider for similarity
MIN_CONTENT_LENGTH = 100

# =============================================================================
# SIMILARITY FUNCTIONS
# =============================================================================


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison.

    - Convert to lowercase
    - Remove extra whitespace
    - Remove punctuation

    Args:
        text: The text to normalize

    Returns:
        Normalized text string
    """
    # Convert to lowercase
    text = text.lower()

    # Remove punctuation and special characters
    text = re.sub(r"[^\w\s]", "", text)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def compute_similarity(text1: str, text2: str) -> float:
    """
    Compute similarity ratio between two texts.

    Uses difflib's SequenceMatcher which is good for fuzzy matching.

    Args:
        text1: First text
        text2: Second text

    Returns:
        Similarity ratio (0.0 to 1.0)
    """
    # Normalize both texts
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)

    # Use SequenceMatcher for fuzzy comparison
    return SequenceMatcher(None, norm1, norm2).ratio()


def compute_hash(content: str) -> str:
    """
    Compute a hash of the content for exact duplicate detection.

    Args:
        content: The content to hash

    Returns:
        SHA-256 hash string
    """
    normalized = normalize_text(content)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


# =============================================================================
# SUBMISSION HANDLING
# =============================================================================


def load_submission(filepath: Path) -> dict | None:
    """
    Load a submission file and extract relevant data.

    Args:
        filepath: Path to the submission file

    Returns:
        Dictionary with submission data or None if failed
    """
    try:
        post = frontmatter.load(filepath)
        return {
            "path": filepath,
            "title": post.metadata.get("title", ""),
            "content": post.content,
            "hash": compute_hash(post.content),
        }
    except Exception as e:
        print(f"Warning: Failed to load {filepath}: {e}")
        return None


def find_all_submissions(base_path: Path) -> list[dict]:
    """
    Find and load all existing submissions.

    Args:
        base_path: Path to the repository root

    Returns:
        List of submission dictionaries
    """
    submissions_dir = base_path / "submissions"
    if not submissions_dir.exists():
        return []

    submissions = []
    for filepath in submissions_dir.glob("**/*.md"):
        sub = load_submission(filepath)
        if sub:
            submissions.append(sub)

    return submissions


# =============================================================================
# DUPLICATE DETECTION
# =============================================================================


def check_duplicate(
    new_submission: dict,
    existing_submissions: list[dict],
) -> tuple[bool, list[dict]]:
    """
    Check if a new submission is a duplicate of any existing ones.

    Args:
        new_submission: The new submission to check
        existing_submissions: List of existing submissions

    Returns:
        Tuple of (is_duplicate, list of similar submissions)
    """
    duplicates = []

    for existing in existing_submissions:
        # Skip comparing to itself (same file path)
        # Use resolve() to handle both absolute and relative paths
        if existing["path"].resolve() == new_submission["path"].resolve():
            continue

        # Check for exact hash match
        if existing["hash"] == new_submission["hash"]:
            duplicates.append(
                {
                    "submission": existing,
                    "reason": "Exact content match",
                    "similarity": 1.0,
                }
            )
            continue

        # Check title similarity
        title_sim = compute_similarity(new_submission["title"], existing["title"])
        if title_sim >= TITLE_SIMILARITY_THRESHOLD:
            duplicates.append(
                {
                    "submission": existing,
                    "reason": f"Similar title ({title_sim:.1%} match)",
                    "similarity": title_sim,
                }
            )
            continue

        # Check content similarity (only if content is long enough)
        if (
            len(new_submission["content"]) >= MIN_CONTENT_LENGTH
            and len(existing["content"]) >= MIN_CONTENT_LENGTH
        ):
            content_sim = compute_similarity(
                new_submission["content"],
                existing["content"],
            )
            if content_sim >= CONTENT_SIMILARITY_THRESHOLD:
                duplicates.append(
                    {
                        "submission": existing,
                        "reason": f"Similar content ({content_sim:.1%} match)",
                        "similarity": content_sim,
                    }
                )

    # Sort by similarity (highest first)
    duplicates.sort(key=lambda x: x["similarity"], reverse=True)

    return len(duplicates) > 0, duplicates


def check_submissions_for_duplicates(
    new_files: list[Path],
    base_path: Path,
) -> tuple[bool, dict]:
    """
    Check multiple new submissions for duplicates.

    Args:
        new_files: List of new submission file paths
        base_path: Path to the repository root

    Returns:
        Tuple of (has_duplicates, dict of results per file)
    """
    # Load all existing submissions
    all_submissions = find_all_submissions(base_path)

    results = {}
    has_duplicates = False

    for filepath in new_files:
        # Load the new submission
        new_sub = load_submission(filepath)
        if not new_sub:
            results[filepath] = {
                "status": "error",
                "message": "Failed to load submission",
            }
            continue

        # Check for duplicates
        is_dup, duplicates = check_duplicate(new_sub, all_submissions)

        if is_dup:
            has_duplicates = True
            results[filepath] = {
                "status": "duplicate",
                "duplicates": duplicates,
            }
        else:
            results[filepath] = {
                "status": "unique",
            }

    return has_duplicates, results


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


def main() -> int:
    """
    Main entry point for the duplicate detection script.

    Returns:
        Exit code (0 for success/no duplicates, 1 for duplicates found)
    """
    # Determine repository root
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent

    # Get files to check from command line args
    if len(sys.argv) > 1:
        files_to_check = [Path(arg) for arg in sys.argv[1:]]
    else:
        # Check all submissions
        submissions_dir = repo_root / "submissions"
        files_to_check = list(submissions_dir.glob("**/*.md")) if submissions_dir.exists() else []

    if not files_to_check:
        print("✅ No files to check for duplicates.")
        return 0

    print(f"🔍 Checking {len(files_to_check)} file(s) for duplicates...\n")

    has_duplicates, results = check_submissions_for_duplicates(
        files_to_check,
        repo_root,
    )

    # Print results
    for filepath, result in results.items():
        print(f"📄 {filepath.name}")

        if result["status"] == "error":
            print(f"   ⚠️  {result['message']}\n")
        elif result["status"] == "unique":
            print("   ✅ No duplicates found\n")
        else:
            print("   ❌ Potential duplicate(s) found:")
            for dup in result["duplicates"]:
                dup_path = dup["submission"]["path"]
                print(f"      • {dup_path.name}")
                print(f"        Reason: {dup['reason']}")
            print()

    # Print summary
    print("=" * 60)
    if has_duplicates:
        print("❌ Potential duplicates detected!")
        print("   Please ensure your submission is unique or significantly different.")
        return 1
    else:
        print("✅ No duplicates found. All submissions are unique!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
