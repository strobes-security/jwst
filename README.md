# JWST (James Webb Screenshot Telescope)

JWST is a tool that analyzes screenshots of websites to identify features and technologies, useful for penetration testing and security assessments. Named after the James Webb Space Telescope, this tool "observes" website screenshots using OpenAI's Vision capabilities to provide detailed analysis and insights.

## Features

- Analyzes website screenshots to identify:
  - Old-looking sites (potential vulnerability targets)
  - Login pages
  - Full web applications
  - Custom 404 pages
  - Parked domains
  - Technologies in use
  - Potential security issues
- Processes entire directories of screenshots in parallel
- Provides results in JSON or tabular format
- Includes confidence scores for each detection

## Installation

```bash
# Clone this repository
git clone https://github.com/yourusername/jwst.git
cd jwst

# Install dependencies
pip install openai requests tqdm rich
```

## Usage

### Basic Usage

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Analyze a directory of screenshots
python jwst.py /path/to/screenshots

# Display results as a formatted table
python jwst.py /path/to/screenshots --format table

# Save results to a JSON file
python jwst.py /path/to/screenshots --output results.json

# Use a different model (if you have access)
python jwst.py /path/to/screenshots --model gpt-4-vision

# Increase parallel processing for faster analysis with many screenshots
python jwst.py /path/to/screenshots --workers 8
```

### Command Line Options

```
usage: jwst.py [-h] [--output OUTPUT] [--format {json,table}]
               [--api-key API_KEY] [--model MODEL] [--workers WORKERS]
               directory

JWST - Analyze website screenshots using OpenAI

positional arguments:
  directory             Directory containing website screenshots

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output file (defaults to stdout)
  --format {json,table}, -f {json,table}
                        Output format (json or table, defaults to json)
  --api-key API_KEY     OpenAI API key (defaults to OPENAI_API_KEY environment variable)
  --model MODEL         OpenAI model to use (defaults to gpt-4-vision-preview)
  --workers WORKERS     Maximum number of parallel workers (defaults to 4)
```

## Example Output

### JSON Format

```json
{
  "screenshot1.png": {
    "old_looking": {
      "detected": true,
      "confidence": 0.95
    },
    "login_page": {
      "detected": true,
      "confidence": 0.88
    },
    "webapp": {
      "detected": true,
      "confidence": 0.92
    },
    "custom_404": {
      "detected": false,
      "confidence": 0.02
    },
    "parked_domain": {
      "detected": false,
      "confidence": 0.01
    },
    "technologies": [
      "PHP",
      "Bootstrap",
      "jQuery",
      "MySQL"
    ],
    "security_issues": [
      "Exposed version information",
      "Outdated framework detected"
    ]
  }
}
```

### Table Format

When using the `--format table` option, JWST will display the results as a rich, colored table in your terminal, making it easy to quickly scan through multiple screenshots.

## Comparison with Original Eyeballer

1. **Name**: Inspired by the James Webb Space Telescope, which observes the deep universe with unprecedented clarity, just as JWST observes websites with enhanced vision capabilities
2. **Technology**: Uses OpenAI's Vision API instead of custom neural networks
3. **Analysis**: Provides more detailed analysis including technology detection and security issues
4. **Setup**: No need for GPU or training data - just requires an OpenAI API key
5. **Output**: Includes confidence scores and more detailed categorization
6. **Processing**: Can process multiple screenshots in parallel

## Requirements

- Python 3.7+
- OpenAI API key with access to Vision models
- Dependencies: openai, requests, tqdm, rich

## License

MIT
