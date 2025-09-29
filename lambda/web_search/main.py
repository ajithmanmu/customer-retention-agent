import json
import logging
from ddgs import DDGS

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def web_search(keywords: str, region: str = "us-en", max_results: int = 5):
    """Search the web for updated information.
    
    Args:
        keywords (str): The search query keywords.
        region (str): The search region: wt-wt, us-en, uk-en, ru-ru, etc.
        max_results (int): The maximum number of results to return.
        
    Returns:
        List of dictionaries with search results.
    """
    try:
        results = DDGS().text(keywords, region=region, max_results=max_results)
        return results if results else []
    except Exception as e:
        logger.error(f"DDGS search error: {str(e)}")
        return []

def lambda_handler(event, context):
    """
    Web Search Lambda function for Customer Retention Agent.
    
    This function provides web search capabilities using DuckDuckGo Search (DDGS)
    to help the retention agent find current information about customer retention
    strategies, industry trends, and best practices.
    
    Args:
        event: Lambda event containing search query and parameters
        context: Lambda context object
        
    Returns:
        dict: Search results in standardized format
    """
    
    try:
        # Handle API Gateway event
        if 'body' in event:
            # API Gateway event - parse JSON body
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            query = body.get('query', '')
            region = body.get('region', 'us-en')
            max_results = body.get('max_results', 5)
        else:
            # Direct invocation event
            query = event.get('query', '')
            region = event.get('region', 'us-en')
            max_results = event.get('max_results', 5)
        
        logger.info(f"Processing web search request for query: {query}")
        
        # Validate input
        if not query or not query.strip():
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Search query is required',
                    'query': query
                })
            }
        
        # Perform web search using DDGS
        search_results = web_search(query, region, max_results)
        
        # Format results for consistent response
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                'title': result.get('title', ''),
                'url': result.get('href', ''),
                'snippet': result.get('body', ''),
                'source': 'web_search'
            })
        
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'query': query,
                'region': region,
                'results': formatted_results,
                'total_results': len(formatted_results),
                'source': 'web_search'
            })
        }
        
        logger.info(f"Successfully processed search request. Found {len(formatted_results)} results.")
        return response
        
    except Exception as e:
        logger.error(f"Error processing web search request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'source': 'web_search'
            })
        }

