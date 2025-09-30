# Churn Data Query Lambda Function

Churn data query Lambda function for the Customer Retention Agent using Amazon Athena.

## Quick Start

### 1. Build
```bash
sam build
```

### 2. Test Locally
```bash
sam local invoke ChurnDataQueryFunction -e events/churn-data-query-event.json
```

### 3. Deploy to AWS
```bash
sam deploy --guided
```

## Input/Output

**Input:**
```json
{
    "customer_id": "3916-NRPAP"
}
```

**Output:**
```json
{
    "statusCode": 200,
    "body": {
        "customer_id": "3916-NRPAP",
        "churn_data": {
            "found": true,
            "churn_analysis": {
                "churn_status": "No",
                "churn_risk_score": 0.45,
                "risk_level": "MEDIUM",
                "cancel_intent": false,
                "abandoned_checkout": false
            },
            "customer_profile": {
                "tenure_months": 12,
                "contract_type": "Month-to-month",
                "monthly_charges": 65.5,
                "total_charges": 780.0,
                "payment_method": "Electronic check",
                "services": {
                    "phone_service": "Yes",
                    "internet_service": "DSL",
                    "online_security": "No",
                    "tech_support": "No"
                }
            },
            "retention_insights": {
                "key_risk_factors": ["Month-to-month contract", "No online security"],
                "recommendations": ["Offer annual contract discount", "Promote online security add-on"]
            }
        }
    }
}
```

## Configuration

- **Runtime**: Python 3.9
- **Memory**: 512 MB
- **Timeout**: 60 seconds
- **Database**: telco_processed_db
- **View**: telco_augmented_vw
