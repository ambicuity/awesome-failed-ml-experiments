#!/usr/bin/env python3
"""
Weekly Summary Generator for Awesome Failed ML Experiments

This script generates a weekly summary including:
- New submissions from the past week
- Common failure patterns
- Statistics and trends
- Top contributors

Runs automatically every Sunday at 03:00 UTC via GitHub Actions.

Author: Ritesh Rana (riteshrana36@gmail.com)
"""

import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

import frontmatter

# =============================================================================
# CONFIGURATION
# =============================================================================

# Category configuration with emojis
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

# Common failure pattern keywords to look for
FAILURE_KEYWORDS = {
    "overfitting": ["overfit", "overfitting", "memoriz"],
    "underfitting": ["underfit", "underfitting", "high bias"],
    "data quality": ["data quality", "noisy data", "mislabeled", "annotation"],
    "small dataset": ["small dataset", "limited data", "few samples", "data scarcity"],
    "hyperparameters": ["hyperparameter", "learning rate", "batch size", "tuning"],
    "architecture": ["architecture", "model size", "layers", "capacity"],
    "training instability": ["nan", "exploding gradient", "vanishing gradient", "unstable"],
    "computational resources": ["memory", "gpu", "oom", "out of memory", "resource"],
    "preprocessing": ["preprocessing", "normalization", "tokenization", "augmentation"],
    "evaluation": ["metric", "evaluation", "test set", "validation", "leakage"],
}

# =============================================================================
# DATA LOADING
# =============================================================================


def load_all_submissions(base_path: Path) -> list[dict]:
    """
    Load all submission files with their content.

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
        try:
            post = frontmatter.load(filepath)

            # Parse date
            date_str = post.metadata.get("date", "")
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                date = datetime.min

            submissions.append(
                {
                    "filepath": filepath,
                    "title": post.metadata.get("title", filepath.stem),
                    "category": post.metadata.get("category", "Other"),
                    "date": date,
                    "date_str": date_str,
                    "author": post.metadata.get("author", "Unknown"),
                    "github": post.metadata.get("github", ""),
                    "content": post.content.lower(),  # Lowercase for pattern matching
                }
            )
        except Exception as e:
            print(f"Warning: Failed to load {filepath}: {e}")

    return submissions


def filter_recent_submissions(
    submissions: list[dict],
    days: int = 7,
) -> list[dict]:
    """
    Filter submissions from the past N days.

    Args:
        submissions: List of all submissions
        days: Number of days to look back

    Returns:
        List of recent submissions
    """
    cutoff = datetime.now() - timedelta(days=days)
    return [s for s in submissions if s["date"] >= cutoff]


# =============================================================================
# PATTERN ANALYSIS
# =============================================================================


def detect_failure_patterns(submissions: list[dict]) -> dict[str, int]:
    """
    Detect common failure patterns in submissions.

    Args:
        submissions: List of submissions with content

    Returns:
        Dictionary mapping pattern names to occurrence counts
    """
    pattern_counts = Counter()

    for sub in submissions:
        content = sub["content"]
        for pattern_name, keywords in FAILURE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content:
                    pattern_counts[pattern_name] += 1
                    break  # Count each pattern once per submission

    return dict(pattern_counts)


def get_category_distribution(submissions: list[dict]) -> dict[str, int]:
    """
    Get the distribution of submissions by category.

    Args:
        submissions: List of submissions

    Returns:
        Dictionary mapping categories to counts
    """
    return Counter(s["category"] for s in submissions)


def get_top_contributors(submissions: list[dict], top_n: int = 5) -> list[tuple[str, int]]:
    """
    Get the top contributors by number of submissions.

    Args:
        submissions: List of submissions
        top_n: Number of top contributors to return

    Returns:
        List of (author, count) tuples
    """
    author_counts = Counter()
    for sub in submissions:
        author = sub["github"] if sub["github"] else sub["author"]
        author_counts[author] += 1

    return author_counts.most_common(top_n)


# =============================================================================
# SUMMARY GENERATION
# =============================================================================


def generate_summary(
    all_submissions: list[dict],
    recent_submissions: list[dict],
    base_path: Path,
) -> str:
    """
    Generate the weekly summary markdown content.

    Args:
        all_submissions: All submissions
        recent_submissions: Submissions from the past week
        base_path: Path to the repository root

    Returns:
        Markdown string for the summary
    """
    now = datetime.now()
    week_start = now - timedelta(days=7)

    lines = [
        "# Weekly Summary 📊",
        "",
        "> Auto-generated summary of new failures and common patterns.",
        "",
        "---",
        "",
        "## 📅 Latest Summary",
        "",
        f"**Week of {week_start.strftime('%B %d')} - {now.strftime('%B %d, %Y')}**",
        "",
    ]

    # New submissions this week
    if recent_submissions:
        lines.extend(
            [
                f"### 🆕 New Submissions ({len(recent_submissions)})",
                "",
            ]
        )
        for sub in recent_submissions:
            rel_path = sub["filepath"].relative_to(base_path)
            emoji = CATEGORIES.get(sub["category"], "🤖")
            author_str = f"@{sub['github']}" if sub["github"] else sub["author"]
            lines.append(f"- {emoji} [{sub['title']}]({rel_path}) by {author_str}")
        lines.append("")
    else:
        lines.extend(
            [
                "### 🆕 New Submissions",
                "",
                "_No new submissions this week._",
                "",
            ]
        )

    # Statistics
    lines.extend(
        [
            "---",
            "",
            "## 📈 Statistics",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Submissions | {len(all_submissions)} |",
            f"| This Week | {len(recent_submissions)} |",
            f"| Categories | {len(CATEGORIES)} |",
            f"| Contributors | {len({s['github'] or s['author'] for s in all_submissions})} |",
            "",
        ]
    )

    # Category distribution
    if all_submissions:
        lines.extend(
            [
                "### 📊 By Category",
                "",
                "| Category | Count |",
                "|----------|-------|",
            ]
        )
        cat_dist = get_category_distribution(all_submissions)
        for category, emoji in CATEGORIES.items():
            count = cat_dist.get(category, 0)
            lines.append(f"| {emoji} {category} | {count} |")
        lines.append("")

    # Common failure patterns
    lines.extend(
        [
            "---",
            "",
            "## 🏷️ Common Failure Patterns",
            "",
        ]
    )

    if all_submissions:
        patterns = detect_failure_patterns(all_submissions)
        if patterns:
            sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
            lines.append("| Pattern | Occurrences |")
            lines.append("|---------|-------------|")
            for pattern, count in sorted_patterns[:10]:
                lines.append(f"| {pattern.title()} | {count} |")
            lines.append("")
        else:
            lines.append("_No clear patterns detected yet._")
            lines.append("")
    else:
        lines.append("_Patterns will be identified once we have more submissions._")
        lines.append("")

    # Top contributors
    if all_submissions:
        lines.extend(
            [
                "---",
                "",
                "## 🏆 Top Contributors",
                "",
            ]
        )
        top_contribs = get_top_contributors(all_submissions)
        if top_contribs:
            lines.append("| Contributor | Submissions |")
            lines.append("|-------------|-------------|")
            for author, count in top_contribs:
                display = f"@{author}" if not author.startswith("@") else author
                lines.append(f"| {display} | {count} |")
            lines.append("")

    # Archive section
    lines.extend(
        [
            "---",
            "",
            "## 📚 Archive",
            "",
            "Previous weekly summaries will be listed here.",
            "",
            "---",
            "",
            '<p align="center">',
            "  <i>Generated automatically every Sunday at 03:00 UTC</i>",
            "</p>",
        ]
    )

    return "\n".join(lines)


def write_summary(base_path: Path, content: str) -> bool:
    """
    Write the summary to WEEKLY_SUMMARY.md.

    Args:
        base_path: Path to the repository root
        content: The summary markdown content

    Returns:
        True if successful
    """
    summary_path = base_path / "WEEKLY_SUMMARY.md"

    try:
        summary_path.write_text(content, encoding="utf-8")
        print("✅ WEEKLY_SUMMARY.md updated successfully")
        return True
    except Exception as e:
        print(f"Error writing summary: {e}")
        return False


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


def main() -> int:
    """
    Main entry point for the weekly summary generator.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Determine repository root
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent

    print("📊 Generating weekly summary...\n")

    # Load submissions
    all_submissions = load_all_submissions(repo_root)
    print(f"Found {len(all_submissions)} total submission(s)")

    recent_submissions = filter_recent_submissions(all_submissions)
    print(f"Found {len(recent_submissions)} submission(s) from the past week")

    # Generate and write summary
    summary = generate_summary(all_submissions, recent_submissions, repo_root)
    success = write_summary(repo_root, summary)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
