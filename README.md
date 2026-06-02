# JSON Lint Tool

A simple, robust command-line tool to validate, format, and lint JSON files.

## Features

- ✅ Validate JSON structure with detailed error reporting (line/column)
- ✅ Format JSON with consistent, configurable indentation
- ✅ Preserve original key order by default (optional `--sort-keys` for alphabetical ordering)
- ✅ Safe by default - refuses to overwrite existing files without `--force`
- ✅ Preserves Unicode/UTF-8 characters (non-ASCII safe)
- ✅ Output defaults to current working directory (not input file location)
- ✅ Zero external dependencies - pure Python standard library
- ✅ Full type hints and comprehensive error handling

## Installation

### Quick start (no installation)
```bash
# Download the script
curl -O https://raw.githubusercontent.com/yourusername/json-lint/main/json_lint.py
chmod +x json_lint.py

# Run directly
./json_lint.py data.json
```

### Global alias (recommended for frequent use)
```bash
# Add to your .bashrc, .zshrc, or .profile
alias jsonlint='python /path/to/json_lint.py'

# Use anywhere
jsonlint data.json --indent 4
```

## Usage

### Basic usage
```bash
# Auto-generates output in current directory: data_linted.json
python json_lint.py data.json

# Specify custom output path
python json_lint.py data.json --output formatted/data.json

# Force overwrite existing output file
python json_lint.py data.json --force
```

### Indentation control
```bash
# 4 spaces instead of default 2
python json_lint.py data.json --indent 4

# Compact JSON (minified, no extra spaces)
python json_lint.py data.json --indent 0

# Short form
python json_lint.py data.json -i 4
```

### Key ordering
```bash
# Default: preserves original key order
python json_lint.py data.json

# Alphabetically sort keys (changes output order)
python json_lint.py data.json --sort-keys
```

### Error handling examples
```bash
# Invalid JSON
$ python json_lint.py invalid.json
Error: Invalid JSON in invalid.json: JSON decode error at line 3, column 10: Expecting property name enclosed in double quotes

# Output file exists without --force
$ python json_lint.py data.json
Error: Output file already exists: ./data_linted.json. Use --force to overwrite.

# Non-existent input
$ python json_lint.py missing.json
Error: Input file does not exist: missing.json
```

## Output location

Output files default to the **current working directory**, not the input file's directory:

| Command | Input location | Output location |
|---------|---------------|-----------------|
| `jsonlint ~/data/data.json` | `/home/user/data/data.json` | `./data_linted.json` |
| `jsonlint ~/data/data.json --output ~/output/clean.json` | `/home/user/data/data.json` | `/home/user/output/clean.json` |

## Output naming scheme

When no output path is specified, the tool auto-generates one in the current directory:

| Input | Output |
|-------|--------|
| `data.json` | `./data_linted.json` |
| `config.geojson` | `./config_linted.geojson` |
| `settings` (no extension) | `./settings_linted.json` |

## Exit codes

- `0` - Success (JSON valid and formatted)
- `1` - Error (invalid JSON, file I/O, permissions, etc.)

## Requirements

- Python 3.7 or higher
- No external packages required

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
