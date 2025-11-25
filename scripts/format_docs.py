#!/usr/bin/env python3
"""
Format and lint Python code snippets in markdown documentation files.

This script:
1. Finds all markdown files in the docs/ directory
2. Extracts Python code blocks (```python ... ```)
3. Formats them with ruff (async for speed)
4. Updates the markdown files with the formatted code
"""

import asyncio
import logging
import re
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def find_markdown_files(docs_dir: Path) -> List[Path]:
    """Find all markdown files in the docs directory."""
    return sorted(docs_dir.rglob("*.md"))


def extract_python_blocks(content: str) -> List[Tuple[str, int, int]]:
    """
    Extract Python code blocks from markdown content.

    Returns:
        List of tuples: (code, start_pos, end_pos)
    """
    pattern = r"```python\n(.*?)```"
    blocks = []

    for match in re.finditer(pattern, content, re.DOTALL):
        code = match.group(1)
        start = match.start()
        end = match.end()
        blocks.append((code, start, end))

    return blocks


async def format_python_code(code: str) -> str:
    """
    Format Python code using ruff (async).

    Args:
        code: Python code string to format

    Returns:
        Formatted code string
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(code)

    try:
        # Format with ruff
        format_proc = await asyncio.create_subprocess_exec(
            "uv",
            "run",
            "ruff",
            "format",
            "--quiet",
            str(tmp_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await format_proc.wait()

        # Fix linting issues
        check_proc = await asyncio.create_subprocess_exec(
            "uv",
            "run",
            "ruff",
            "check",
            "--fix",
            "--quiet",
            str(tmp_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await check_proc.wait()

        # Read the formatted and fixed code
        formatted_code = tmp_path.read_text()

        return formatted_code

    except Exception as e:
        # If formatting fails, return original code
        logger.warning("Failed to format code: %s", e)
        return code

    finally:
        # Clean up temp file
        tmp_path.unlink(missing_ok=True)


async def update_markdown_with_formatted_code(
    content: str, blocks: List[Tuple[str, int, int]]
) -> str:
    """
    Update markdown content with formatted code blocks (async).

    Args:
        content: Original markdown content
        blocks: List of (code, start_pos, end_pos) tuples

    Returns:
        Updated markdown content
    """
    if not blocks:
        return content

    # Format all blocks concurrently
    format_tasks = [format_python_code(code) for code, _, _ in blocks]
    formatted_codes = await asyncio.gather(*format_tasks)

    # Apply formatting results
    result = content
    offset = 0

    for (original_code, start, end), formatted_code in zip(blocks, formatted_codes):
        # Remove trailing newline if original didn't have one
        if not original_code.endswith("\n"):
            formatted_code = formatted_code.rstrip("\n")

        # Construct the new block
        new_block = f"```python\n{formatted_code}```"
        original_block = content[start:end]

        # Only update if there's a difference
        if new_block != original_block:
            result = result[: start + offset] + new_block + result[end + offset :]
            offset += len(new_block) - len(original_block)

    return result


async def process_markdown_file(
    file_path: Path, dry_run: bool = False
) -> Tuple[Path, bool]:
    """
    Process a single markdown file (async).

    Args:
        file_path: Path to markdown file
        dry_run: If True, don't write changes

    Returns:
        Tuple of (file_path, changed)
    """
    content = file_path.read_text()
    blocks = extract_python_blocks(content)

    if not blocks:
        return (file_path, False)

    # Create updated content
    updated_content = await update_markdown_with_formatted_code(content, blocks)

    if updated_content == content:
        return (file_path, False)

    if not dry_run:
        # Write updated content
        file_path.write_text(updated_content)

    return (file_path, True)


async def main():
    """Main entry point."""
    # Parse arguments
    dry_run = "--dry-run" in sys.argv

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    docs_dir = project_root / "docs"

    if not docs_dir.exists():
        logger.error("docs directory not found at %s", docs_dir)
        sys.exit(1)

    logger.info("Formatting Python snippets in: %s", docs_dir)
    if dry_run:
        logger.info("DRY RUN MODE - No files will be modified")
    logger.info("")

    # Find all markdown files
    markdown_files = find_markdown_files(docs_dir)

    if not markdown_files:
        logger.info("No markdown files found")
        sys.exit(0)

    logger.info("Found %d markdown file(s)", len(markdown_files))
    logger.info("Processing all files concurrently...\n")

    # Process all files concurrently
    tasks = [process_markdown_file(file_path, dry_run) for file_path in markdown_files]
    results = await asyncio.gather(*tasks)

    # Collect changed files and log results
    changed_files = []
    for file_path, changed in results:
        status = (
            "✓ Updated"
            if changed and not dry_run
            else "→ Would update"
            if changed
            else "  No changes"
        )
        blocks = extract_python_blocks(file_path.read_text())
        rel_path = file_path.relative_to(project_root)

        if blocks:
            logger.info("%s %s (%d blocks)", f"{status:12}", rel_path, len(blocks))
        else:
            logger.info("  No blocks  %s", rel_path)

        if changed:
            changed_files.append(file_path)

    # Summary
    logger.info("\n" + "=" * 60)
    if changed_files:
        action = "would be updated" if dry_run else "updated"
        logger.info("%d file(s) %s:", len(changed_files), action)
        for file_path in changed_files:
            logger.info("  - %s", file_path.relative_to(project_root))
    else:
        logger.info("No files needed formatting changes")

    if dry_run and changed_files:
        logger.info("\nRun without --dry-run to apply changes")


if __name__ == "__main__":
    asyncio.run(main())
