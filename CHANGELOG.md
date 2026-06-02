# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-06-02

### Changed
- **Breaking**: Output path changed from positional argument to `--output` / `-o` flag
  - Old: `jsonlint input.json output.json`
  - New: `jsonlint input.json --output output.json`
  - Auto-generation behavior unchanged (no flag = auto-generates to cwd)

### Added
- Short form `-o` for specifying output path
- `--replace` / `-r` flag for in-place file modification
  - Implies `--force` (no need for separate force flag)
  - Mutually exclusive with `--output`

## [0.1.0] - 2026-06-01

### Added
- Initial release
- JSON validation with line/column error reporting
- JSON formatting with configurable indentation (0-16 spaces, default 2)
- Optional output path with auto-generation using `{stem}_linted{extension}` naming scheme
- `--force` flag to overwrite existing output files
- `--indent` / `-i` parameter for space-based indentation control
- Sorted object keys for consistent, diff-friendly output
- UTF-8 encoding support with preservation of non-ASCII characters
- Comprehensive error handling for:
  - Missing input files
  - Permission errors
  - Unicode decode errors
  - Invalid JSON structure
  - Existing output file conflicts
- Path handling via `pathlib` (no string path manipulation)
- Full type hints and docstrings for all functions
- Proper exit codes (0 success, 1 error)
- MIT License

### Technical Details
- Pure Python standard library - no external dependencies
- Compatible with Python 3.7+
- Single-file implementation for easy distribution
- Follows Unix conventions (success to stdout, errors to stderr)

[0.1.0]: https://github.com/bkuz114/json-lint/releases/tag/v0.1.0
