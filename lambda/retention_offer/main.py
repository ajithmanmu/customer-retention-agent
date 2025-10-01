import json
import logging
import random
from typing import Dict, List, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def generate_discount_coupons(customer_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate discount coupon offers for high-risk customers.
    
    Args:
        customer_profile: Customer profile data
        
    Returns:
        List of discount coupon offers
    """
    monthly_charges = customer_profile.get('monthly_charges', 0)
    tenure_months = customer_profile.get('tenure_months', 0)
    
    offers = []
    
    # High-value discount for immediate retention
    if monthly_charges > 70:
        offers.append({
            "offer_type": "discount_coupon",
            "code": f"SAVE{random.randint(20, 30)}",
            "title": f"{random.randint(20, 30)}% Off Next 3 Months",
            "description": f"Save {random.randint(20, 30)}% on your monthly bill for the next 3 months",
            "discount_percentage": random.randint(20, 30),
            "validity_days": 90,
            "priority": "high"
        })
    else:
        offers.append({
            "offer_type": "discount_coupon",
            "code": f"SAVE{random.randint(15, 25)}",
            "title": f"{random.randint(15, 25)}% Off Next 2 Months",
            "description": f"Save {random.randint(15, 25)}% on your monthly bill for the next 2 months",
            "discount_percentage": random.randint(15, 25),
            "validity_days": 60,
            "priority": "medium"
        })
    
    # Annual contract discount
    if customer_profile.get('contract_type') == 'Month-to-month':
        offers.append({
            "offer_type": "contract_discount",
            "code": f"ANNUAL{random.randint(40, 50)}",
            "title": f"{random.randint(40, 50)}% Off Annual Contract",
            "description": f"Switch to annual contract and save {random.randint(40, 50)}%",
            "discount_percentage": random.randint(40, 50),
            "validity_days": 30,
            "priority": "high"
        })
    
    return offers

def generate_service_offers(customer_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate service-based offers for medium/low-risk customers.
    
    Args:
        customer_profile: Customer profile data
        
    Returns:
        List of service offers
    """
    offers = []
    
    # Free service add-ons
    service_offers = [
        {
            "service": "online_security",
            "title": "Free Online Security",
            "description": "3 months free online security add-on",
            "value": 15.0,
            "validity_days": 90
        },
        {
            "service": "tech_support",
            "title": "Free Premium Tech Support",
            "description": "6 months free premium tech support",
            "value": 20.0,
            "validity_days": 180
        },
        {
            "service": "streaming_tv",
            "title": "Free Streaming TV",
            "description": "2 months free streaming TV service",
            "value": 25.0,
            "validity_days": 60
        }
    ]
    
    # Select 1-2 random service offers
    selected_offers = random.sample(service_offers, min(2, len(service_offers)))
    
    for offer in selected_offers:
        offers.append({
            "offer_type": "service_upgrade",
            "code": f"FREE{offer['service'].upper()[:6]}",
            "title": offer['title'],
            "description": offer['description'],
            "service": offer['service'],
            "value": offer['value'],
            "validity_days": offer['validity_days'],
            "priority": "medium"
        })
    
    return offers

def generate_retention_offers(customer_id: str, churn_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate personalized retention offers based on churn risk data.
    
    Args:
        customer_id: Customer ID
        churn_data: Churn analysis data from churn_data_query Lambda
        
    Returns:
        Dict containing retention offers and recommendations
    """
    try:
        churn_analysis = churn_data.get('churn_analysis', {})
        customer_profile = churn_data.get('customer_profile', {})
        
        risk_level = churn_analysis.get('risk_level', 'LOW')
        churn_risk_score = churn_analysis.get('churn_risk_score', 0)
        
        logger.info(f"Generating offers for customer {customer_id} with risk level: {risk_level}")
        
        offers = []
        recommended_action = ""
        
        # Risk-based offer generation
        if risk_level == "HIGH":
            # High risk = immediate discount coupons
            offers = generate_discount_coupons(customer_profile)
            recommended_action = "Present discount offers immediately - customer is at high risk of churning"
            
        elif risk_level == "MEDIUM":
            # Medium risk = mix of discounts and service offers
            discount_offers = generate_discount_coupons(customer_profile)
            service_offers = generate_service_offers(customer_profile)
            offers = discount_offers[:1] + service_offers[:1]  # Take 1 of each
            recommended_action = "Present mixed offers - customer shows moderate churn risk"
            
        else:  # LOW risk
            # Low risk = service offers and loyalty rewards
            offers = generate_service_offers(customer_profile)
            recommended_action = "Present service upgrades - customer is stable but could benefit from additional services"
        
        # Add urgency based on risk score
        if churn_risk_score > 0.8:
            for offer in offers:
                offer['urgency'] = 'immediate'
                offer['description'] += " - Limited time offer!"
        elif churn_risk_score > 0.6:
            for offer in offers:
                offer['urgency'] = 'high'
        else:
            for offer in offers:
                offer['urgency'] = 'normal'
        
        response = {
            'customer_id': customer_id,
            'risk_level': risk_level,
            'churn_risk_score': churn_risk_score,
            'offers': offers,
            'total_offers': len(offers),
            'recommended_action': recommended_action,
            'offer_strategy': f"Risk-based strategy for {risk_level} risk customer"
        }
        
        logger.info(f"Generated {len(offers)} offers for customer {customer_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating retention offers: {str(e)}")
        raise

def lambda_handler(event, context):
    """
    Retention Offer Lambda function for Customer Retention Agent.
    
    This function generates personalized retention offers based on churn risk data
    to help retain customers who are at risk of churning.
    
    Args:
        event: Lambda event containing customer ID and churn data
        context: Lambda context object
        
    Returns:
        dict: Retention offers in standardized format
    """
    
    try:
        # Handle API Gateway event
        if 'body' in event:
            # API Gateway event - parse JSON body
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            customer_id = body.get('customer_id', '')
            churn_data = body.get('churn_data', {})
        else:
            # Direct invocation event
            customer_id = event.get('customer_id', '')
            churn_data = event.get('churn_data', {})
        
        logger.info(f"Processing retention offer request for customer: {customer_id}")
        
        # Validate input
        if not customer_id or not customer_id.strip():
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Customer ID is required',
                    'customer_id': customer_id
                })
            }
        
        if not churn_data:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Churn data is required',
                    'customer_id': customer_id
                })
            }
        
        # Generate retention offers
        retention_offers = generate_retention_offers(customer_id.strip(), churn_data)
        
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'customer_id': customer_id,
                'retention_offers': retention_offers,
                'source': 'retention_offer'
            })
        }
        
        logger.info(f"Successfully generated retention offers for customer: {customer_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing retention offer request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'source': 'retention_offer'
            })
        }
