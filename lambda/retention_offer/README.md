# Retention Offer Lambda Function

Retention offer Lambda function for the Customer Retention Agent that generates personalized offers based on churn risk data.

## Quick Start

### 1. Build
```bash
sam build
```

### 2. Test Locally
```bash
sam local invoke RetentionOfferFunction -e events/retention-offer-event.json
```

### 3. Deploy to AWS
```bash
sam deploy --guided
```

## Input/Output

**Input:**
```json
{
    "customer_id": "3916-NRPAP",
    "churn_data": {
        "churn_analysis": {
            "churn_risk_score": 0.75,
            "risk_level": "HIGH",
            "cancel_intent": true
        },
        "customer_profile": {
            "tenure_months": 2,
            "contract_type": "Month-to-month",
            "monthly_charges": 85.0
        }
    }
}
```

**Output:**
```json
{
    "statusCode": 200,
    "body": {
        "customer_id": "3916-NRPAP",
        "retention_offers": {
            "risk_level": "HIGH",
            "offers": [
                {
                    "offer_type": "discount_coupon",
                    "code": "SAVE25",
                    "title": "25% Off Next 3 Months",
                    "description": "Save 25% on your monthly bill for the next 3 months",
                    "discount_percentage": 25,
                    "validity_days": 90,
                    "urgency": "immediate"
                }
            ],
            "recommended_action": "Present discount offers immediately - customer is at high risk of churning"
        }
    }
}
```

## Risk-Based Offer Strategy

- **HIGH Risk**: Discount coupons (20-30% off)
- **MEDIUM Risk**: Mixed offers (discounts + service upgrades)
- **LOW Risk**: Service upgrades and loyalty rewards

## Configuration

- **Runtime**: Python 3.9
- **Memory**: 256 MB
- **Timeout**: 30 seconds
