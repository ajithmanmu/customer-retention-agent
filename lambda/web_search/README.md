# Web Search Lambda Function

Web search Lambda function for the Customer Retention Agent using DuckDuckGo Search.

## Quick Start

### 1. Build
```bash
sam build
```

### 2. Test Locally
```bash
sam local invoke WebSearchFunction -e events/web-search-event.json
```

### 3. Deploy to AWS
```bash
sam deploy --guided
```

## Input/Output

**Input:**
```json
{
    "query": "customer retention strategies 2024",
    "region": "us-en",
    "max_results": 3
}
```

**Output:**
```json
{
    "statusCode": 200,
    "body": {
        "query": "customer retention strategies 2024",
        "results": [
            {
                "title": "Customer Retention Strategies",
                "url": "https://example.com",
                "snippet": "Guide to retention...",
                "source": "web_search"
            }
        ],
        "total_results": 1
    }
}
```

## Configuration

- **Runtime**: Python 3.9
- **Memory**: 256 MB
- **Timeout**: 30 seconds
