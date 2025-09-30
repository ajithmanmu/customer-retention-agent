import json
import logging
import boto3
from typing import Dict, List, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
athena_client = boto3.client('athena')
s3_client = boto3.client('s3')

def execute_athena_query(query: str, database: str, output_location: str) -> Dict[str, Any]:
    """
    Execute an Athena query and return results.
    
    Args:
        query (str): SQL query to execute
        database (str): Athena database name
        output_location (str): S3 location for query results
        
    Returns:
        Dict containing query results and metadata
    """
    try:
        # Start query execution
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': database},
            ResultConfiguration={'OutputLocation': output_location}
        )
        
        query_execution_id = response['QueryExecutionId']
        logger.info(f"Started Athena query execution: {query_execution_id}")
        
        # Wait for query to complete
        while True:
            response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            status = response['QueryExecution']['Status']['State']
            
            if status in ['SUCCEEDED']:
                break
            elif status in ['FAILED', 'CANCELLED']:
                error_reason = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
                raise Exception(f"Query failed: {error_reason}")
            
            # Wait 2 seconds before checking again
            import time
            time.sleep(2)
        
        # Get query results
        results_response = athena_client.get_query_results(QueryExecutionId=query_execution_id)
        
        # Parse results
        rows = results_response['ResultSet']['Rows']
        if len(rows) < 2:  # Less than header + 1 data row
            return {'results': [], 'row_count': 0}
        
        # Extract column names from first row
        columns = [col['VarCharValue'] for col in rows[0]['Data']]
        
        # Extract data rows
        results = []
        for row in rows[1:]:  # Skip header row
            row_data = {}
            for i, col in enumerate(row['Data']):
                value = col.get('VarCharValue', '')
                row_data[columns[i]] = value
            results.append(row_data)
        
        return {
            'results': results,
            'row_count': len(results),
            'columns': columns,
            'query_execution_id': query_execution_id
        }
        
    except Exception as e:
        logger.error(f"Athena query execution failed: {str(e)}")
        raise

def get_customer_churn_data(customer_id: str) -> Dict[str, Any]:
    """
    Get churn data for a specific customer from Athena.
    
    Args:
        customer_id (str): Customer ID to query
        
    Returns:
        Dict containing customer churn data and risk analysis
    """
    try:
        # Athena configuration
        database = 'telco_processed_db'
        output_location = 's3://aws-athena-query-results-us-east-1-412602263780/'
        
        # Query to get customer data from the augmented view
        query = f"""
        SELECT 
            customerid,
            gender,
            seniorcitizen,
            partner,
            dependents,
            tenure,
            phoneservice,
            multiplelines,
            internetservice,
            onlinesecurity,
            onlinebackup,
            deviceprotection,
            techsupport,
            streamingtv,
            streamingmovies,
            paperlessbilling,
            paymentmethod,
            monthlycharges,
            totalcharges,
            churn,
            contract,
            status,
            churn_risk_score,
            cancel_intent
        FROM telco_augmented_vw 
        WHERE customerid = '{customer_id}'
        """
        
        logger.info(f"Executing churn data query for customer: {customer_id}")
        
        # Execute query
        query_result = execute_athena_query(query, database, output_location)
        
        if query_result['row_count'] == 0:
            return {
                'customer_id': customer_id,
                'found': False,
                'message': 'Customer not found in database'
            }
        
        # Get customer data (should be only one row)
        customer_data = query_result['results'][0]
        
        # Analyze churn risk
        churn_risk_score = float(customer_data.get('churn_risk_score', 0))
        cancel_intent = customer_data.get('cancel_intent', 'false').lower() == 'true'
        churn_status = customer_data.get('churn', 'No')
        
        # Determine risk level
        if churn_risk_score >= 0.7:
            risk_level = 'HIGH'
        elif churn_risk_score >= 0.4:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        # Format response
        response = {
            'customer_id': customer_id,
            'found': True,
            'churn_analysis': {
                'churn_status': churn_status,
                'churn_risk_score': churn_risk_score,
                'risk_level': risk_level,
                'cancel_intent': cancel_intent
            },
            'customer_profile': {
                'tenure_months': int(customer_data.get('tenure', 0)),
                'contract_type': customer_data.get('contract', ''),
                'monthly_charges': float(customer_data.get('monthlycharges', 0)),
                'total_charges': float(customer_data.get('totalcharges', 0)),
                'payment_method': customer_data.get('paymentmethod', ''),
                'paperless_billing': customer_data.get('paperlessbilling', ''),
                'services': {
                    'phone_service': customer_data.get('phoneservice', ''),
                    'internet_service': customer_data.get('internetservice', ''),
                    'online_security': customer_data.get('onlinesecurity', ''),
                    'tech_support': customer_data.get('techsupport', ''),
                    'streaming_tv': customer_data.get('streamingtv', ''),
                    'streaming_movies': customer_data.get('streamingmovies', '')
                }
            },
            'retention_insights': {
                'key_risk_factors': [],
                'recommendations': []
            }
        }
        
        # Identify key risk factors
        risk_factors = []
        if customer_data.get('contract') == 'Month-to-month':
            risk_factors.append('Month-to-month contract')
        if int(customer_data.get('tenure', 0)) <= 3:
            risk_factors.append('Low tenure (≤3 months)')
        if customer_data.get('onlinesecurity') == 'No':
            risk_factors.append('No online security')
        if customer_data.get('techsupport') == 'No':
            risk_factors.append('No tech support')
        if float(customer_data.get('monthlycharges', 0)) > 80:
            risk_factors.append('High monthly charges')
        
        response['retention_insights']['key_risk_factors'] = risk_factors
        
        # Generate recommendations based on risk factors
        recommendations = []
        if 'Month-to-month contract' in risk_factors:
            recommendations.append('Offer annual contract discount')
        if 'Low tenure' in risk_factors:
            recommendations.append('Provide onboarding support and welcome offers')
        if 'No online security' in risk_factors:
            recommendations.append('Promote online security add-on')
        if 'High monthly charges' in risk_factors:
            recommendations.append('Review service bundle and offer discounts')
        
        response['retention_insights']['recommendations'] = recommendations
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting customer churn data: {str(e)}")
        raise

def lambda_handler(event, context):
    """
    Churn Data Query Lambda function for Customer Retention Agent.
    
    This function queries customer churn data from Athena to provide
    churn risk analysis and retention insights for the retention agent.
    
    Args:
        event: Lambda event containing customer ID and query parameters
        context: Lambda context object
        
    Returns:
        dict: Customer churn data and analysis in standardized format
    """
    
    try:
        # Handle API Gateway event
        if 'body' in event:
            # API Gateway event - parse JSON body
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            customer_id = body.get('customer_id', '')
        else:
            # Direct invocation event
            customer_id = event.get('customer_id', '')
        
        logger.info(f"Processing churn data query for customer: {customer_id}")
        
        # Validate input
        if not customer_id or not customer_id.strip():
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Customer ID is required',
                    'customer_id': customer_id
                })
            }
        
        # Get customer churn data
        churn_data = get_customer_churn_data(customer_id.strip())
        
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'customer_id': customer_id,
                'churn_data': churn_data,
                'source': 'churn_data_query'
            })
        }
        
        logger.info(f"Successfully processed churn data query for customer: {customer_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing churn data query: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'source': 'churn_data_query'
            })
        }
