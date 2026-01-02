#!/usr/bin/env python3
"""
README Updater for Awesome Failed ML Experiments

This script automatically updates README.md with:
- Categorized list of all submissions
- Recent submissions section
- Statistics

The README is regenerated from scratch each time to ensure consistency.

Author: Ritesh Rana (riteshrana36@gmail.com)
"""

import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import frontmatter

# =============================================================================
# CONFIGURATION
# =============================================================================

# Category configuration with emojis and order
CATEGORIES = {
    "Computer Vision": "🖼️",
    "Natural Language Processing": "📝",
    "Speech & Audio": "🔊",
    "Tabular Data": "📊",
    "Reinforcement Learning": "🎮",
    "Generative Models": "🧬",
    "Time Series": "⏱️",
    "Anomaly Detection": "🔍",
    "Recommendation Systems": "📈",
    "MLOps & Infrastructure": "🔧",
    "Other": "🤖",
}

# Number of recent submissions to show
NUM_RECENT = 10

# Markers in README for auto-generated content
CATEGORIES_START = "<!-- AUTO-GENERATED CATEGORIES START -->"
CATEGORIES_END = "<!-- AUTO-GENERATED CATEGORIES END -->"
RECENT_START = "<!-- AUTO-GENERATED RECENT START -->"
RECENT_END = "<!-- AUTO-GENERATED RECENT END -->"

# =============================================================================
# SUBMISSION HANDLING
# =============================================================================


def load_all_submissions(base_path: Path) -> list[dict]:
    """
    Load all submission files and extract metadata.

    Args:
        base_path: Path to the repository root

    Returns:
        List of submission dictionaries sorted by date (newest first)
    """
    submissions_dir = base_path / "submissions"
    if not submissions_dir.exists():
        return []

    submissions = []
    for filepath in submissions_dir.glob("**/*.md"):
        try:
            post = frontmatter.load(filepath)

            # Calculate relative path from repo root for links
            rel_path = filepath.relative_to(base_path)

            # Parse date
            date_str = post.metadata.get("date", "")
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                date = datetime.min

            submissions.append(
                {
                    "path": rel_path,
                    "filepath": filepath,
                    "title": post.metadata.get("title", filepath.stem),
                    "category": post.metadata.get("category", "Other"),
                    "date": date,
                    "date_str": date_str,
                    "author": post.metadata.get("author", "Unknown"),
                    "github": post.metadata.get("github", ""),
                }
            )
        except Exception as e:
            print(f"Warning: Failed to load {filepath}: {e}")

    # Sort by date (newest first)
    submissions.sort(key=lambda x: x["date"], reverse=True)

    return submissions


def group_by_category(submissions: list[dict]) -> dict:
    """
    Group submissions by their category.

    Args:
        submissions: List of submission dictionaries

    Returns:
        Dictionary mapping category names to lists of submissions
    """
    grouped = defaultdict(list)

    for sub in submissions:
        category = sub["category"]
        # Ensure category is valid
        if category not in CATEGORIES:
            category = "Other"
        grouped[category].append(sub)

    return grouped


# =============================================================================
# README GENERATION
# =============================================================================


def generate_categories_section(submissions: list[dict]) -> str:
    """
    Generate the categories section of the README.

    Args:
        submissions: List of all submissions

    Returns:
        Markdown string for the categories section
    """
    grouped = group_by_category(submissions)

    lines = []

    # Generate each category section in order
    for category, emoji in CATEGORIES.items():
        lines.append(f"### {emoji} {category}")

        category_subs = grouped.get(category, [])

        if not category_subs:
            lines.append("_No submissions yet in this category._")
        else:
            for sub in category_subs:
                # Format: - [Title](path) by @author (date)
                author_str = f"@{sub['github']}" if sub["github"] else sub["author"]
                lines.append(
                    f"- [{sub['title']}]({sub['path']}) by {author_str} ({sub['date_str']})"
                )

        lines.append("")  # Empty line between categories

    return "\n".join(lines).rstrip()


def generate_recent_section(submissions: list[dict]) -> str:
    """
    Generate the recent submissions section.

    Args:
        submissions: List of all submissions (already sorted by date)

    Returns:
        Markdown string for the recent section
    """
    if not submissions:
        return "_No submissions yet. Be the first to share your failure!_"

    recent = submissions[:NUM_RECENT]

    lines = []
    for sub in recent:
        emoji = CATEGORIES.get(sub["category"], "🤖")
        author_str = f"@{sub['github']}" if sub["github"] else sub["author"]
        lines.append(
            f"- {emoji} [{sub['title']}]({sub['path']}) by {author_str} ({sub['date_str']})"
        )

    return "\n".join(lines)


def update_readme_section(
    content: str,
    start_marker: str,
    end_marker: str,
    new_content: str,
) -> str:
    """
    Update a section of the README between markers.

    Args:
        content: The full README content
        start_marker: The start marker comment
        end_marker: The end marker comment
        new_content: The new content to insert

    Returns:
        Updated README content
    """
    # Find the markers
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        print(f"Warning: Markers not found in README ({start_marker})")
        return content

    # Build the new content
    before = content[: start_idx + len(start_marker)]
    after = content[end_idx:]

    return f"{before}\n{new_content}\n{after}"


def update_readme(base_path: Path) -> bool:
    """
    Update the README.md file with current submissions.

    Args:
        base_path: Path to the repository root

    Returns:
        True if update was successful
    """
    readme_path = base_path / "README.md"

    if not readme_path.exists():
        print("Error: README.md not found")
        return False

    try:
        content = readme_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading README: {e}")
        return False

    # Load all submissions
    submissions = load_all_submissions(base_path)
    print(f"Found {len(submissions)} submission(s)")

    # Generate new sections
    categories_content = generate_categories_section(submissions)
    recent_content = generate_recent_section(submissions)

    # Update the README
    content = update_readme_section(
        content,
        CATEGORIES_START,
        CATEGORIES_END,
        categories_content,
    )
    content = update_readme_section(
        content,
        RECENT_START,
        RECENT_END,
        recent_content,
    )

    # Write back
    try:
        readme_path.write_text(content, encoding="utf-8")
        print("✅ README.md updated successfully")
        return True
    except Exception as e:
        print(f"Error writing README: {e}")
        return False


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


def main() -> int:
    """
    Main entry point for the README updater script.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Determine repository root
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent

    print("📝 Updating README.md...\n")

    success = update_readme(repo_root)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
