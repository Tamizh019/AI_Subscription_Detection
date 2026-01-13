from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import numpy as np
from datetime import timedelta
from typing import Dict
from ml_features import extract_ml_features, features_to_array
from ml_detector import SubscriptionDetector

app = FastAPI()
ml_detector = SubscriptionDetector()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= CONFIGURATION =============
CATEGORY_KEYWORDS = {
    "Entertainment": ["netflix", "prime video", "hotstar", "spotify", "youtube premium", 
                     "apple music", "hulu", "disney", "audible", "zee5", "sonyliv", "voot",
                     "clash of clans", "jiohotstar", "hotstaron"],
    "Software": ["adobe", "github", "aws", "google workspace", "microsoft 365", "jetbrains", 
                "notion", "slack", "zoom", "chatgpt", "openai", "canva pro", "dropbox", 
                "google one", "fastspring", "valve", "google play", "playstore", "google cloud"],
    "Food/Groceries": ["swiggy one", "zomato pro", "zomato", "swiggy", "blinkit", "zepto"],
    "Utilities": ["electricity", "bescom", "water", "bwssb", "gas", "jio fiber", "jio recharge",
                 "airtel postpaid", "airtel prepaid", "airtel recharge", "vodafone", "act fibernet", 
                 "bsnl", "tata sky", "tata play", "bharti airtel", "bharti a", "airtelprep", "airtel"],
    "Finance": ["sip", "mutual fund", "insurance", "premium", "loan", "emi", "zerodha", 
               "groww", "hdfc life", "lic", "icici pru", "smallcase"]
}

NON_SUBSCRIPTION_MERCHANTS = [
    "flipkart", "amazon.in", "amazon i", "myntra", "ajio", "reliance digital", 
    "croma", "decathlon", "dmart", "bigbasket", "uber", "ola", "rapido",
    "paytm", "phonepe", "gpay", "google pay", "bookmyshow", "apollo", 
    "medplus", "starbucks", "cafe", "grocery", "kirana", "tea stall", 
    "petrol", "atm", "cash", "suresh", "udaygiri", "backiam", "pradeepr", "kalees"
]

SUBSCRIPTION_KEYWORDS = [
    "membership", "subscription", "premium", "pro", "plus", "recharge", "postpaid", "prepaid",
    "insurance", "sip", "emi", "electricity", "water", "fiber", 
    "netflix", "spotify", "prime", "hotstar", "youtube premium", "jiohotstar", "hotstaron",
    "adobe", "github", "chatgpt", "canva", "notion", "microsoft", "smallcase",
    "google one", "fastspring", "valve", "clash of clans", "google cloud", "airtel", "bharti"
]

# ============= HELPER FUNCTIONS =============
def preprocess_bank_statement(content: str) -> str:
    """Remove bank statement header rows"""
    lines = content.split('\n')
    header_keywords = ['date', 'description', 'particulars', 'narration', 'details', 
                       'debit', 'amount', 'withdrawal', 'merchant', 'transaction',
                       'credit', 'balance', 'cheque', 'ref no']
    
    start_index = 0
    for i, line in enumerate(lines):
        lower_line = line.lower()
        keyword_count = sum(1 for keyword in header_keywords if keyword in lower_line)
        if keyword_count >= 3:
            start_index = i
            break
    
    return '\n'.join(lines[start_index:])

def smart_column_detection(df: pd.DataFrame) -> Dict[str, str]:
    """Auto-detect date, description, and amount columns"""
    columns = [c.lower().strip() for c in df.columns]
    mapping = {}
    
    # Date column
    date_keywords = ['date', 'transaction_date', 'trans_date', 'txn_date', 'time', 'dt']
    for col in columns:
        if any(keyword in col for keyword in date_keywords):
            mapping['date'] = df.columns[columns.index(col)]
            break
    
    # Description column
    desc_keywords = ['description', 'narration', 'particulars', 'merchant', 
                     'merchant_name', 'details', 'transaction_description', 'remarks']
    for col in columns:
        if any(keyword in col for keyword in desc_keywords):
            mapping['description'] = df.columns[columns.index(col)]
            break
    
    # Amount column (debit first)
    amount_keywords = ['debit', 'withdrawal', 'amount', 'transaction_amount', 'debit_amount', 'dr']
    for col in columns:
        if any(keyword in col for keyword in amount_keywords):
            mapping['amount'] = df.columns[columns.index(col)]
            break
    
    return mapping

def clean_merchant_name(description: str) -> str:
    """Extract clean merchant name from UPI/bank transaction"""
    if pd.isna(description):
        return ""
    
    desc = str(description).strip().upper()
    
    # Remove prefixes
    prefixes = ['WDL TFR', 'DEP TFR', 'UPI/DR/', 'UPI/CR/', 'UPI/', 'POS ATM PURCH',
                'IMPS/', 'NEFT/', 'RTGS/', 'ATM WDL', 'CSH DEP', 'OTHPG']
    for prefix in prefixes:
        if prefix in desc:
            desc = desc.split(prefix)[-1].strip()
    
    # Extract from UPI format
    if '/' in desc:
        parts = [p.strip() for p in desc.split('/') if p.strip()]
        banks = ['YESB', 'HDFC', 'ICIC', 'SBIN', 'UTIB', 'PAYTM', 'AIRP', 'CNRB', 
                'UBIN', 'IOBA', 'IDIB', 'CBIN', 'INDB', 'RATN']
        
        for part in parts:
            if len(part) > 3 and not part.isdigit() and part not in banks:
                return part.strip()
    
    # Remove long numbers
    words = desc.split()
    cleaned_words = [w for w in words if not (w.isdigit() and len(w) > 8)]
    
    result = ' '.join(cleaned_words[:3]) if cleaned_words else desc[:50]
    return result.strip()

def is_likely_subscription(description: str) -> bool:
    """Check if merchant name suggests subscription"""
    desc_lower = description.lower()
    
    # Exclude personal transfers
    personal_names = ["suresh", "udaygiri", "backiam", "pradeepr", "kalees", 
                     "ashwin", "dilsh", "kisho", "mr m", "mr "]
    if any(name in desc_lower for name in personal_names):
        return False
    
    has_subscription_keyword = any(keyword in desc_lower for keyword in SUBSCRIPTION_KEYWORDS)
    is_shopping_site = any(merchant in desc_lower for merchant in NON_SUBSCRIPTION_MERCHANTS)
    
    if "swiggy one" in desc_lower or "zomato pro" in desc_lower:
        return True
    
    if is_shopping_site and not has_subscription_keyword:
        return False
    
    return has_subscription_keyword

def get_category(description: str) -> str:
    """Categorize merchant"""
    desc_lower = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(k in desc_lower for k in keywords):
            return category
    return "Other"

def determine_pattern_type(confidence_label: str, frequency: str) -> str:
    """Classify as subscription or pattern"""
    if confidence_label == "High":
        return "subscription"
    if confidence_label == "Medium" and frequency in ["Monthly", "Quarterly", "Yearly", "Half-yearly", "Weekly"]:
        return "subscription"
    return "pattern"

def generate_pattern_description(avg_interval: int, category: str) -> str:
    """Generate human-readable pattern description"""
    if category == "Food/Groceries":
        return "Frequent orders detected"
    if avg_interval <= 10:
        return "You spend here almost daily"
    elif avg_interval <= 30:
        return f"You spend here every ~{int(avg_interval)} days"
    else:
        return f"Regular spending pattern (~{int(avg_interval)} days)"

def predict_next_date(last_date: pd.Timestamp, days_freq: float) -> str:
    """Predict next payment date"""
    next_date = last_date + timedelta(days=int(days_freq))
    return str(next_date.date())

# ============= API ENDPOINTS =============
@app.get("/")
def read_root():
    return {"message": "SubDetect AI - Universal Bank Statement Analyzer", "version": "3.0"}

@app.post("/analyze")
async def analyze_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")

    try:
        # 1. Load and preprocess
        content = await file.read()
        raw_content = content.decode('utf-8')
        cleaned_content = preprocess_bank_statement(raw_content)
        df = pd.read_csv(io.StringIO(cleaned_content))

        # 2. Detect columns
        column_mapping = smart_column_detection(df)
        
        if not all(k in column_mapping for k in ['date', 'description', 'amount']):
            return {
                "error": "Could not detect required columns (Date, Description, Amount)",
                "detected_columns": list(df.columns)
            }

        # 3. Rename columns
        df = df.rename(columns={
            column_mapping['date']: 'date',
            column_mapping['description']: 'description',
            column_mapping['amount']: 'amount'
        })

        # 4. Data cleaning
        df['date'] = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)
        df = df.dropna(subset=['date', 'amount'])
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df = df[df['amount'] > 0]
        
        if len(df) < 10:
            return {"error": "Not enough valid transactions", "found_transactions": len(df)}
        
        # 5. Clean merchant names
        df['description'] = df['description'].apply(clean_merchant_name)
        
        # 6. ML Clustering
        unique_descs = df['description'].unique().tolist()
        merchant_mapping = ml_detector.cluster_merchants(unique_descs)
        df['unified_merchant'] = df['description'].map(merchant_mapping)
        
        detected_items = []
        
        # 7. Analyze each merchant group
        for merchant, group in df.groupby('unified_merchant'):
            if len(group) < 3:
                continue
            
            if not is_likely_subscription(merchant):
                continue
            
            group = group.sort_values('date')
            features = extract_ml_features(group)
            
            if features is None:
                continue
            
            features_array = features_to_array(features)
            ml_prediction, ml_score = ml_detector.detect_subscription_pattern(features_array)
            
            if ml_prediction != 1:
                continue
            
            confidence_score, confidence_label = ml_detector.calculate_confidence(features, ml_score)
            
            # RELAXED FILTERS - Accept patterns with low confidence
            if confidence_score < 0.05:  # Only reject extremely low
                continue
            
            category = get_category(merchant)
            avg_interval = features['avg_interval_days']
            
            if avg_interval < 20 or avg_interval > 400:
                continue
            
            # Determine frequency
            if 25 <= avg_interval <= 35:
                frequency = "Monthly"
            elif 360 <= avg_interval <= 375:
                frequency = "Yearly"
            elif 6 <= avg_interval <= 8:
                frequency = "Weekly"
            elif 85 <= avg_interval <= 95:
                frequency = "Quarterly"
            elif 175 <= avg_interval <= 185:
                frequency = "Half-yearly"
            else:
                frequency = f"Every {int(avg_interval)} days"
            
            dates = group['date']
            amounts = group['amount']
            last_amount = amounts.iloc[-1]
            avg_amount = amounts.mean()
            
            pattern_type = determine_pattern_type(confidence_label, frequency)
            pattern_description = generate_pattern_description(avg_interval, category)
            
            # Risk analysis
            risk = "Safe"
            risk_reasons = []
            
            if last_amount > avg_amount * 1.15:
                risk = "Medium"
                risk_reasons.append(f"Price increased by {int((last_amount/avg_amount - 1)*100)}%")
            
            if last_amount > 2000 and category == "Entertainment":
                risk = "High" if risk == "Medium" else "Medium"
                risk_reasons.append("High cost for Entertainment")
            
            if last_amount > 5000:
                risk = "High"
                risk_reasons.append("Expensive subscription")
            
            days_since_last = features['days_since_last']
            expected_next = avg_interval + 7
            
            if days_since_last > expected_next:
                status = "Potentially Inactive"
                risk = "Medium" if risk == "Safe" else risk
                risk_reasons.append(f"No payment for {days_since_last} days")
            else:
                status = "Active"
            
            detected_items.append({
                "Description": group.iloc[0]['description'],
                "UnifiedName": merchant.title(),
                "Amount": float(last_amount),
                "AvgAmount": float(avg_amount),
                "LastDate": str(dates.iloc[-1].date()),
                "NextDate": predict_next_date(dates.iloc[-1], avg_interval),
                "Frequency": frequency,
                "Category": category,
                "Risk": risk,
                "RiskReasons": risk_reasons,
                "Confidence": confidence_label,
                "ConfidenceScore": round(confidence_score * 100, 1),
                "Status": status,
                "TransactionCount": len(group),
                "MLScore": round(float(ml_score), 3),
                "PatternType": pattern_type,
                "PatternDescription": pattern_description
            })

        # Sort by amount
        detected_items.sort(key=lambda x: x['Amount'], reverse=True)

        # Separate subscriptions and patterns
        subscriptions = [s for s in detected_items if s['PatternType'] == 'subscription']
        patterns = [s for s in detected_items if s['PatternType'] == 'pattern']

        # Calculate insights
        total_monthly = sum(s['Amount'] for s in subscriptions if s['Frequency'] == "Monthly")
        total_yearly_estimate = sum(
            s['Amount'] * 12 if s['Frequency'] == "Monthly" 
            else s['Amount'] * 52 if s['Frequency'] == "Weekly"
            else s['Amount'] * 4 if s['Frequency'] == "Quarterly"
            else s['Amount'] * 2 if s['Frequency'] == "Half-yearly"
            else s['Amount']
            for s in subscriptions
        )
        
        high_risk_count = sum(1 for s in subscriptions if s['Risk'] == "High")
        medium_risk_count = sum(1 for s in subscriptions if s['Risk'] == "Medium")
        
        return {
            "status": "success",
            "message": f"Detected {len(subscriptions)} subscriptions and {len(patterns)} patterns.",
            "subscriptions": detected_items,
            "insights": {
                "total_subscriptions": len(subscriptions),
                "total_patterns": len(patterns),
                "total_monthly_cost": round(total_monthly, 2),
                "estimated_yearly_cost": round(total_yearly_estimate, 2),
                "high_risk_count": high_risk_count,
                "medium_risk_count": medium_risk_count,
                "categories": list(set(s['Category'] for s in subscriptions)),
                "avg_confidence": round(np.mean([s['ConfidenceScore'] for s in subscriptions]), 1) if subscriptions else 0
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Analysis failed: {str(e)}"}
