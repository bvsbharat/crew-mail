# User Details Research Crew

This CrewAI-powered crew researches comprehensive professional information about individuals using their email address and name. It uses multiple AI agents and search tools to gather, validate, and structure user data.

## Features

- **Multi-Agent Research**: Uses specialized agents for different research tasks
- **Multiple Data Sources**: Integrates EXA and Serper search APIs
- **Data Validation**: Cross-references information from multiple sources
- **Structured Output**: Returns clean, validated user profiles
- **CLI Interface**: Easy-to-use command-line interface

## Prerequisites

1. **Environment Variables**: Ensure the following are set in your `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   EXA_API_KEY=your_exa_api_key
   SERPER_API_KEY=your_serper_api_key
   ```

2. **Python Dependencies**: Install required packages (should be available in the project's virtual environment)

## Usage

### Command Line Interface

Run the crew using the main.py script:

```bash
# Basic usage
python main.py --email "user@example.com" --name "John Doe"

# With different output formats
python main.py --email "user@example.com" --name "John Doe" --output-format json
python main.py --email "user@example.com" --name "John Doe" --output-format summary
python main.py --email "user@example.com" --name "John Doe" --output-format pretty

# Force refresh existing data
python main.py --email "user@example.com" --name "John Doe" --force-refresh

# Verbose output for debugging
python main.py --email "user@example.com" --name "John Doe" --verbose

# Email only (name is optional but recommended)
python main.py --email "user@example.com"
```

### Available Options

- `--email`: Email address of the person to research (required)
- `--name`: Name of the person to research (optional but recommended)
- `--force-refresh`: Force refresh even if user details already exist
- `--output-format`: Choose output format (json, pretty, summary)
- `--verbose`: Enable verbose output for debugging
- `--help`: Show help message

### Output Formats

1. **Pretty** (default): Human-readable formatted output
2. **JSON**: Machine-readable JSON format
3. **Summary**: Brief summary of key information

## Examples

### Example 1: Research a Known User
```bash
python main.py --email "marco@vapi.ai" --name "Marco Bariani"
```

### Example 2: JSON Output for Integration
```bash
python main.py --email "user@company.com" --output-format json
```

### Example 3: Force Refresh Existing Data
```bash
python main.py --email "user@company.com" --name "User Name" --force-refresh
```

## Testing

Use the test script to verify the crew is working:

```bash
python test_crew.py
```

## Architecture

The crew consists of three specialized agents:

1. **User Research Agent**: Uses EXA search to find professional information
2. **Serper Research Agent**: Uses Google Search API for additional verification
3. **Data Validation Agent**: Validates, merges, and structures the collected data

## Data Sources

The crew searches for information from:
- LinkedIn profiles
- Company websites
- Professional networking sites
- News articles and mentions
- Social media profiles
- Industry publications

## Output Data Structure

The crew returns structured user profiles containing:
- Full name and email
- Current company and job title
- Professional bio/summary
- Social media URLs (LinkedIn, Twitter, website)
- Location and industry information
- Data quality metrics and source attribution

## Integration

This crew is designed to integrate with the larger email auto-responder system and can be called programmatically:

```python
from user_details_crew import UserDetailsCrew

crew = UserDetailsCrew()
user_details = crew.fetch_user_details(
    email="user@example.com",
    name="User Name",
    force_refresh=False
)
```

## Troubleshooting

1. **API Key Errors**: Ensure all required API keys are set in the `.env` file
2. **Import Errors**: Make sure you're running from the correct directory with proper Python path
3. **Timeout Issues**: Some searches may take time; use the timeout command if needed
4. **Rate Limiting**: Be mindful of API rate limits when making multiple requests

## Notes

- The crew automatically checks for existing user data before initiating new searches
- Results are cached to avoid redundant API calls
- The system prioritizes recent and reliable information sources
- Cross-referencing helps ensure data accuracy and completeness