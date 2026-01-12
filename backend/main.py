from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
from typing import List, Dict

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Subscription Detection API is running"}

@app.post("/analyze")
async def analyze_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")

    print(f"Processing file: {file.filename}") # Debug log

    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

        # Basic Cleaning: Standardize columns
        # Expected columns (case insensitive, loose matching): "Date", "Description", "Debit"
        df.columns = [c.strip().lower() for c in df.columns]
        
        # Map common names to standard names
        col_map = {
            'date': 'date',
            'transaction date': 'date',
            'description': 'description',
            'transaction details': 'description',
            'particulars': 'description',
            'debit': 'amount',
            'withdrawal amount': 'amount',
            'amount': 'amount'
        }
        
        # Renaissance - Rename columns if they exist in map
        current_cols = df.columns
        new_names = {}
        for col in current_cols:
            if col in col_map:
                new_names[col] = col_map[col]
        
        df = df.rename(columns=new_names)

        # Validate required columns
        required = ['date', 'description', 'amount']
        missing = [c for c in required if c not in df.columns]
        
        # If 'amount' suggests both credit/debit, ensure we filter for debits if needed
        # For this MVP, assuming 'amount' col exists and contains debits.
        # If there is a 'credit' column and 'debit' column, we prioritize 'debit'.
        
        if missing:
             return {"error": f"Missing columns: {missing}. Please ensure CSV has Date, Description, and Debit Amount."}

        # Convert Date
        df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['date'])

        # --- SUBSCRIPTION DETECTION LOGIC ---
        
        # 1. Clean Description (Simple normalization)
        df['clean_desc'] = df['description'].str.upper().str.replace(r'\d+', '', regex=True).str.strip()
        
        detected_subs = []
        
        # Group by Description
        grouped = df.groupby('clean_desc')
        
        for desc, group in grouped:
            if len(group) < 2:
                continue
            
            # Sort by date
            group = group.sort_values('date')
            dates = group['date']
            
            # Calculate days between transactions
            diffs = dates.diff().dt.days.dropna()
            
            avg_diff = diffs.mean()
            std_diff = diffs.std() if len(diffs) > 1 else 0
            
            # Criteria for Monthly Subscription:
            # - Average gap ~30 days (25 to 35)
            # - Low variance (std_diff < 5 days) OR just consistency
            
            is_monthly = 25 <= avg_diff <= 35
            is_yearly = 360 <= avg_diff <= 370
            
            if is_monthly or is_yearly:
                # Use the last transaction details
                last_txn = group.iloc[-1]
                avg_amount = group['amount'].mean()
                
                # Risk Logic (Simple)
                # High Risk: High Amount (> 1000) AND Old (First txn > 6 months ago)
                duration_days = (dates.max() - dates.min()).days
                is_old = duration_days > 180
                is_expensive = avg_amount > 500
                
                risk = "Low"
                if is_expensive and is_old:
                    risk = "High"
                elif is_expensive or is_old:
                    risk = "Medium"
                
                detected_subs.append({
                    "Description": desc, # specific
                    "Amount": float(last_txn['amount']),
                    "Date": str(last_txn['date'].date()),
                    "Frequency": "Monthly" if is_monthly else "Yearly",
                    "Risk": risk,
                    "AvgAmount": float(avg_amount)
                })

        return {
            "status": "success",
            "message": f"Found {len(detected_subs)} subscriptions",
            "preview": detected_subs
        }

    except Exception as e:
        print(f"Error processing CSV: {e}")
        return {"error": str(e)}
