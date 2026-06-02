#!/usr/bin/env python3
"""
JSON Lint Tool - A utility for validating, formatting, and rewriting JSON files.

This tool reads a JSON file, validates its structure, and reformats it with
consistent indentation. It includes safety features to prevent accidental
overwrites and provides flexible output options.

# Basic usage - auto-generates output name
python json_lint.py data.json
# Creates: data_linted.json

# With custom output path
python json_lint.py data.json --output formatted/data.json

# Overwrite input file with formatted output
python json_lint.py data.json --replace

# Auto-generated name with custom indent
python json_lint.py data.json --indent 4
# Creates: data_linted.json with 4-space indent

# Force overwrite of auto-generated file
python json_lint.py data.json --force
# Overwrites data_linted.json if it exists

# Works with different extensions
python json_lint.py config.geojson
# Creates: config_linted.geojson

# Works with files without extensions (adds .json)
python json_lint.py myconfig
# Creates: myconfig_linted.json
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Optional, Tuple, Any


def generate_default_output_path(input_path: Path) -> Path:
    """
    Generate a default output path based on the input filename.

    The naming scheme is: {stem}_linted{extension}
    Example: input.json -> input_linted.json

    Args:
        input_path: Path object for the input file

    Returns:
        Path object for the default output location in the same directory
    """
    stem = input_path.stem  # Filename without extension (e.g., "data" from "data.json")
    extension = input_path.suffix  # Extension including dot (e.g., ".json")

    # Handle case where there's no extension
    if not extension:
        extension = ".json"

    return Path.cwd() / f"{stem}_linted{extension}"


def validate_json_content(content: str) -> Any:
    """
    Validate if a string contains valid JSON.

    Args:
        content: String content to validate as JSON

    Returns:
        Any: Parsed JSON data
    """
    try:
        parsed_data = json.loads(content)
        return parsed_data
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"JSON decode error at line {e.lineno}, column {e.colno}: {e.msg}"
        ) from e


def read_json_file(file_path: Path) -> Tuple[str, Any]:
    """
    Read and validate a JSON file.

    Args:
        file_path: Path object pointing to the JSON file

    Returns:
        A tuple containing:
            - str: File content as string if successful
            - Any: Parsed JSON data if successful

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read due to permissions
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {file_path}")

    if not file_path.is_file():
        raise Exception(f"Path is not a file: {file_path}")

    content = file_path.read_text(encoding="utf-8")
    parsed_data = validate_json_content(content)

    return content, parsed_data


def write_json_file(
    file_path: Path, data: Any, indent_spaces: int, sort_keys: bool, force: bool
) -> Path:
    """
    Write formatted JSON data to a file with safety checks.

    Args:
        file_path: Path object for the output file
        data: Python data structure to write as JSON
        indent_spaces: Number of spaces for JSON indentation
        sort_keys: If True, sort object keys alphabetically
        force: If True, overwrite existing files; if False, fail on existing files

    Returns:
        Path: path to output file written
    """
    # Resolve output path to absolute
    # (note: strict=False prevents error if parent path doesn't exist yet)
    file_path = file_path.resolve(strict=False)

    # Check if output file exists and handle according to force flag
    if file_path.exists() and not force:
        raise FileExistsError(
            f"Output file already exists: {file_path}. Use --force to overwrite."
        )

    # Create parent directories if they don't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Write formatted JSON
    formatted_json = json.dumps(
        data,
        indent=indent_spaces,
        ensure_ascii=False,  # Preserve non-ASCII characters
        sort_keys=sort_keys,
    )
    file_path.write_text(formatted_json + "\n", encoding="utf-8")
    return file_path


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the JSON lint tool.

    Returns:
        argparse.Namespace object containing parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="JSON Lint Tool - Validate and format JSON files with consistent indentation.",
        epilog="""Examples:
  %(prog)s input.json                    # Creates input_linted.json
  %(prog)s input.json output.json        # Saves to output.json
  %(prog)s input.json --indent 4         # 4-space indent, default output name
  %(prog)s input.json --force            # Overwrites existing default output
  %(prog)s input.json --sort-keys        # Alphabetically sort object keys""",
    )

    parser.add_argument(
        "input", type=Path, help="Path to the input JSON file to validate and format"
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Path where the formatted JSON will be saved (optional: defaults to {input_stem}_linted{input_extension})",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite of output file if it already exists",
    )

    parser.add_argument(
        "--indent",
        "-i",
        type=int,
        default=2,
        choices=range(0, 17),  # Reasonable indent range: 0-16 spaces
        metavar="SPACES",
        help="Number of spaces for JSON indentation (default: 2, range: 0-16)",
    )

    parser.add_argument(
        "--sort-keys",
        action="store_true",
        help="Sort object keys alphabetically (WARNING: changes output order)",
    )

    parser.add_argument(
        "--replace",
        "-r",
        action="store_true",
        help="Replace the source file in-place (cannot be used with --output)",
    )

    return parser.parse_args()


def main() -> None:
    """
    Main entry point for the JSON lint tool.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    # Parse command-line arguments
    args = parse_arguments()

    # resolve input to absolute (handles rel, symlinks)
    # (rel will be evaluated rel caller cwd, not script dir)
    # note: don't resolve args.output yet as could be None, and
    # resolve will fail if path doesn't exist yet.
    input_path = args.input.resolve()

    # Validate mutual exclusion
    if args.replace and args.output:
        raise ValueError("Error: --replace and --output cannot be used together")

    # Determine output path (generate default if not provided)
    if args.replace:
        output_path = input_path
    elif args.output:
        output_path = args.output
    else:
        output_path = generate_default_output_path(input_path)
        print(f"Note: No output path specified. Using default: {output_path}")

    # Validate indent argument range (though argparse should handle this)
    if args.indent < 0:
        raise ValueError("Error: Indent spaces cannot be negative.")

    # Read and validate input file
    content, parsed_data = read_json_file(input_path)

    # Ensure we have parsed data (should be valid at this point)
    if parsed_data is None:
        raise Exception("Error: Failed to parse JSON data despite validation success.")

    # Write formatted JSON to output file
    written_path = write_json_file(
        output_path,
        parsed_data,
        args.indent,
        args.sort_keys,
        args.force or args.replace,
    )

    # Success message
    action = "replaced" if args.replace else "created"
    print(f"Successfully linted and formatted JSON:")
    print(f"  Input:  {input_path}")
    print(f"  Output: {written_path} ({action})")
    print(f"  Indent: {args.indent} spaces")
    if args.sort_keys:
        print(f"  Note: Object keys were sorted alphabetically (--sort-keys enabled)")


if __name__ == "__main__":
    main()
