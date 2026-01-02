#!/usr/bin/env python3
"""
Submission Validator for Awesome Failed ML Experiments

This script validates new submission files to ensure they meet all requirements:
- Required frontmatter fields (title, category, date, author, github)
- Required markdown sections
- Valid category selection
- Proper file naming conventions

Author: Ritesh Rana (riteshrana36@gmail.com)
"""

import re
import sys
from pathlib import Path

import frontmatter

# =============================================================================
# CONFIGURATION
# =============================================================================

# Valid categories for submissions
VALID_CATEGORIES = [
    "Computer Vision",
    "Natural Language Processing",
    "Speech & Audio",
    "Tabular Data",
    "Reinforcement Learning",
    "Generative Models",
    "Time Series",
    "Anomaly Detection",
    "Recommendation Systems",
    "MLOps & Infrastructure",
    "Other",
]

# Required frontmatter fields with their expected types
REQUIRED_FRONTMATTER = {
    "title": str,
    "category": str,
    "date": str,
    "author": str,
    "github": str,
}

# Required sections in the markdown content (as they appear in headers)
REQUIRED_SECTIONS = [
    "Description",
    "Model / Algorithm",
    "Dataset",
    "What Failed",
    "Why It Failed",
    "Logs / Metrics",
    "Lessons Learned",
]

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================


def validate_filename(filepath: Path) -> list[str]:
    """
    Validate the submission filename follows conventions.

    Rules:
    - Must be .md extension
    - Must use lowercase
    - Must use underscores instead of spaces
    - Must be in a submissions/YEAR/ directory

    Args:
        filepath: Path to the submission file

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check file extension
    if filepath.suffix.lower() != ".md":
        errors.append(f"File must have .md extension, got: {filepath.suffix}")

    # Check for lowercase (excluding extension)
    stem = filepath.stem
    if stem != stem.lower():
        errors.append(f"Filename must be lowercase: {stem} -> {stem.lower()}")

    # Check for spaces
    if " " in stem:
        errors.append(f"Filename must not contain spaces, use underscores: {stem}")

    # Check directory structure (should be submissions/YEAR/)
    parts = filepath.parts
    if "submissions" not in parts:
        errors.append("File must be in submissions/ directory")
    else:
        submissions_idx = parts.index("submissions")
        if len(parts) <= submissions_idx + 1:
            errors.append("File must be in submissions/YEAR/ subdirectory")
        else:
            year_dir = parts[submissions_idx + 1]
            # Check if it's a valid year format (4 digits)
            if not re.match(r"^\d{4}$", year_dir):
                errors.append(f"Year directory must be 4 digits: {year_dir}")

    return errors


def validate_frontmatter(post: frontmatter.Post) -> list[str]:
    """
    Validate the frontmatter (YAML header) of a submission.

    Checks:
    - All required fields are present
    - Fields have correct types
    - Category is valid
    - Date is in correct format

    Args:
        post: Parsed frontmatter Post object

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    metadata = post.metadata

    # Check for required fields
    for field, expected_type in REQUIRED_FRONTMATTER.items():
        if field not in metadata:
            errors.append(f"Missing required frontmatter field: {field}")
        elif not isinstance(metadata[field], expected_type):
            errors.append(
                f"Field '{field}' must be {expected_type.__name__}, "
                f"got {type(metadata[field]).__name__}"
            )

    # Validate category if present
    if (
        "category" in metadata
        and isinstance(metadata["category"], str)
        and metadata["category"] not in VALID_CATEGORIES
    ):
        errors.append(
            f"Invalid category: '{metadata['category']}'. "
            f"Valid categories: {', '.join(VALID_CATEGORIES)}"
        )

    # Validate date format (YYYY-MM-DD)
    if "date" in metadata and isinstance(metadata["date"], str):
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, metadata["date"]):
            errors.append(f"Date must be in YYYY-MM-DD format, got: {metadata['date']}")

    return errors


def validate_sections(content: str) -> list[str]:
    """
    Validate that all required sections are present in the markdown content.

    Args:
        content: The markdown content (without frontmatter)

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Extract all headers from the content
    # Match both ## and ### style headers, and headers with emojis
    header_pattern = r"^#{1,6}\s+(.+)$"
    headers = re.findall(header_pattern, content, re.MULTILINE)

    # Clean headers: remove emojis and extra whitespace
    cleaned_headers = []
    for header in headers:
        # Remove common emojis used in our template
        cleaned = re.sub(r"[📝🤖📊❌🔍📈💡🔗]", "", header)
        cleaned = cleaned.strip()
        cleaned_headers.append(cleaned)

    # Check for required sections
    for section in REQUIRED_SECTIONS:
        found = any(section.lower() in h.lower() for h in cleaned_headers)
        if not found:
            errors.append(f"Missing required section: {section}")

    return errors


def validate_content_quality(content: str) -> list[str]:
    """
    Validate the quality/completeness of content in each section.

    Checks:
    - Sections have meaningful content (not just placeholder text)
    - Minimum content length

    Args:
        content: The markdown content (without frontmatter)

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check for placeholder text that was not replaced
    placeholder_patterns = [
        r"Your .+ here",
        r"e\.g\.,\s*$",
        r"TODO",
        r"FIXME",
        r"\[.*\]\(link\)",
        r"if applicable\)",
    ]

    for pattern in placeholder_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            errors.append(f"Content contains placeholder text matching pattern: {pattern}")

    # Check minimum content length (excluding frontmatter)
    # A good submission should have at least 500 characters of content
    if len(content.strip()) < 500:
        errors.append(
            f"Content too short ({len(content.strip())} chars). "
            "Minimum 500 characters required for a meaningful submission."
        )

    return errors


def validate_submission(filepath: Path) -> tuple[bool, list[str]]:
    """
    Validate a single submission file.

    Args:
        filepath: Path to the submission file

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    # Check if file exists
    if not filepath.exists():
        return False, [f"File not found: {filepath}"]

    # Validate filename
    errors.extend(validate_filename(filepath))

    # Parse the frontmatter
    try:
        post = frontmatter.load(filepath)
    except Exception as e:
        return False, errors + [f"Failed to parse frontmatter: {e}"]

    # Validate frontmatter
    errors.extend(validate_frontmatter(post))

    # Validate sections
    errors.extend(validate_sections(post.content))

    # Validate content quality
    errors.extend(validate_content_quality(post.content))

    return len(errors) == 0, errors


def find_new_submissions(base_path: Path) -> list[Path]:
    """
    Find all submission files that need to be validated.

    In CI, this would typically compare against the base branch.
    For simplicity, this finds all .md files in submissions/.

    Args:
        base_path: Path to the repository root

    Returns:
        List of paths to submission files
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
    Main entry point for the validation script.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Determine repository root
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent

    # Get files to validate from command line args or find all
    if len(sys.argv) > 1:
        files_to_validate = [Path(arg) for arg in sys.argv[1:]]
    else:
        files_to_validate = find_new_submissions(repo_root)

    if not files_to_validate:
        print("✅ No submission files to validate.")
        return 0

    print(f"🔍 Validating {len(files_to_validate)} submission(s)...\n")

    all_valid = True
    for filepath in files_to_validate:
        print(f"📄 Checking: {filepath.name}")

        is_valid, errors = validate_submission(filepath)

        if is_valid:
            print("   ✅ Valid\n")
        else:
            all_valid = False
            print(f"   ❌ Invalid - {len(errors)} error(s):")
            for error in errors:
                print(f"      • {error}")
            print()

    # Print summary
    print("=" * 60)
    if all_valid:
        print("✅ All submissions are valid!")
        return 0
    else:
        print("❌ Some submissions have errors. Please fix them and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
