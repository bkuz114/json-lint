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


def validate_json_content(content: str) -> Tuple[bool, Optional[str], Optional[Any]]:
    """
    Validate if a string contains valid JSON.

    Args:
        content: String content to validate as JSON

    Returns:
        A tuple containing:
            - bool: True if valid JSON, False otherwise
            - Optional[str]: Error message if invalid, None if valid
            - Optional[Any]: Parsed JSON data if valid, None if invalid
    """
    try:
        parsed_data = json.loads(content)
        return True, None, parsed_data
    except json.JSONDecodeError as e:
        error_msg = f"JSON decode error at line {e.lineno}, column {e.colno}: {e.msg}"
        return False, error_msg, None


def read_json_file(
    file_path: Path,
) -> Tuple[Optional[str], Optional[str], Optional[Any]]:
    """
    Read and validate a JSON file.

    Args:
        file_path: Path object pointing to the JSON file

    Returns:
        A tuple containing:
            - Optional[str]: File content as string if successful
            - Optional[str]: Error message if failed
            - Optional[Any]: Parsed JSON data if successful

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read due to permissions
    """
    if not file_path.exists():
        return None, f"Input file does not exist: {file_path}", None

    if not file_path.is_file():
        return None, f"Path is not a file: {file_path}", None

    try:
        content = file_path.read_text(encoding="utf-8")
        is_valid, error_msg, parsed_data = validate_json_content(content)

        if not is_valid:
            return None, f"Invalid JSON in {file_path}: {error_msg}", None

        return content, None, parsed_data

    except PermissionError as e:
        return None, f"Permission denied when reading {file_path}: {e}", None
    except UnicodeDecodeError as e:
        return None, f"File encoding error (expected UTF-8): {e}", None
    except Exception as e:
        return None, f"Unexpected error reading {file_path}: {e}", None


def write_json_file(
    file_path: Path, data: Any, indent_spaces: int, sort_keys: bool, force: bool
) -> Tuple[bool, Optional[str]]:
    """
    Write formatted JSON data to a file with safety checks.

    Args:
        file_path: Path object for the output file
        data: Python data structure to write as JSON
        indent_spaces: Number of spaces for JSON indentation
        sort_keys: If True, sort object keys alphabetically
        force: If True, overwrite existing files; if False, fail on existing files

    Returns:
        A tuple containing:
            - bool: True if write successful, False otherwise
            - Optional[str]: Error message if failed, None if successful
    """
    # Check if output file exists and handle according to force flag
    if file_path.exists() and not force:
        return (
            False,
            f"Output file already exists: {file_path}. Use --force to overwrite.",
        )

    # Create parent directories if they don't exist
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return False, f"Failed to create output directory {file_path.parent}: {e}"

    # Write formatted JSON
    try:
        formatted_json = json.dumps(
            data,
            indent=indent_spaces,
            ensure_ascii=False,  # Preserve non-ASCII characters
            sort_keys=sort_keys,
        )
        file_path.write_text(formatted_json + "\n", encoding="utf-8")
        return True, None
    except TypeError as e:
        return False, f"Data serialization error: {e}"
    except PermissionError as e:
        return False, f"Permission denied when writing to {file_path}: {e}"
    except Exception as e:
        return False, f"Unexpected error writing to {file_path}: {e}"


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
        "input", type=str, help="Path to the input JSON file to validate and format"
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
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

    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the JSON lint tool.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Convert to Path objects
    input_path = Path(args.input)

    # Determine output path (generate default if not provided)
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = generate_default_output_path(input_path)
        print(f"Note: No output path specified. Using default: {output_path}")

    # Validate indent argument range (though argparse should handle this)
    if args.indent < 0:
        print("Error: Indent spaces cannot be negative.", file=sys.stderr)
        return 1

    # Read and validate input file
    content, error_msg, parsed_data = read_json_file(input_path)

    if error_msg:
        print(f"Error: {error_msg}", file=sys.stderr)
        return 1

    # Ensure we have parsed data (should be valid at this point)
    if parsed_data is None:
        print(
            "Error: Failed to parse JSON data despite validation success.",
            file=sys.stderr,
        )
        return 1

    # Write formatted JSON to output file
    success, write_error = write_json_file(
        output_path, parsed_data, args.indent, args.sort_keys, args.force
    )

    if not success:
        print(f"Error: {write_error}", file=sys.stderr)
        return 1

    # Success message
    print(f"Successfully linted and formatted JSON:")
    print(f"  Input:  {input_path}")
    print(f"  Output: {output_path}")
    print(f"  Indent: {args.indent} spaces")
    if args.sort_keys:
        print(f"  Note: Object keys were sorted alphabetically (--sort-keys enabled)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
