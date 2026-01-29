"""
Database Operations
Handles all CSV data operations and crop database management
"""

import pandas as pd
import os
import re
import time
import logging
from config import CSV_FN, USERS_FILE, FEEDBACK_FILE

# ==========================
#  LOAD CROPS DATA
# ==========================
if not os.path.exists(CSV_FN):
    logging.error(f"❌ crops.csv not found at {CSV_FN}")
    logging.error("Please place your crops.csv file in the same directory as backend.py")
    logging.error("Expected columns: seed, soil, season, states, info, growth_days, fertilizers, irrigation")
    exit(1)

try:
    df = pd.read_csv(CSV_FN, dtype=str).fillna("")
    logging.info(f"✅ Loaded {len(df)} crop rows from your dataset")
    logging.info(f"Dataset columns: {list(df.columns)}")
    
    # Validate required columns
    required_cols = ['seed', 'soil', 'season', 'states']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logging.warning(f"⚠ Missing columns in crops.csv: {missing_cols}")
        logging.warning("The system will work with available columns, but functionality may be limited")
    
except Exception as e:
    logging.error(f"❌ Error loading crops.csv: {e}")
    logging.error("Please check your crops.csv file format and content")
    exit(1)

# ==========================
#  USERS & FEEDBACK
# ==========================
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["username", "password", "lang", "created_at", "last_login"]).to_csv(USERS_FILE, index=False)

if not os.path.exists(FEEDBACK_FILE):
    pd.DataFrame(columns=["username", "rating", "feedback", "timestamp"]).to_csv(FEEDBACK_FILE, index=False)

def load_users():
    """Load users from CSV file"""
    try:
        u_df = pd.read_csv(USERS_FILE, dtype=str).fillna("")
        return {row["username"].lower(): {
            "password": row["password"], 
            "lang": row["lang"],
            "created_at": row.get("created_at", ""),
            "last_login": row.get("last_login", "")
        } for _, row in u_df.iterrows()}
    except Exception:
        return {}

def save_users(users_dict):
    """Save users to CSV file"""
    try:
        pd.DataFrame([
            {
                "username": u, 
                "password": users_dict[u]["password"], 
                "lang": users_dict[u]["lang"],
                "created_at": users_dict[u].get("created_at", ""),
                "last_login": users_dict[u].get("last_login", "")
            }
            for u in users_dict
        ]).to_csv(USERS_FILE, index=False)
    except Exception as e:
        logging.error(f"Error saving users: {e}")

def save_feedback(username, rating, feedback_text):
    """Save user feedback to CSV file"""
    try:
        # Load existing feedback
        if os.path.exists(FEEDBACK_FILE):
            feedback_df = pd.read_csv(FEEDBACK_FILE)
        else:
            feedback_df = pd.DataFrame(columns=["username", "rating", "feedback", "timestamp"])
        
        # Add new feedback
        new_feedback = pd.DataFrame([{
            "username": username,
            "rating": rating,
            "feedback": feedback_text,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }])
        
        feedback_df = pd.concat([feedback_df, new_feedback], ignore_index=True)
        feedback_df.to_csv(FEEDBACK_FILE, index=False)
        return True
    except Exception as e:
        logging.error(f"Error saving feedback: {e}")
        return False

# ==========================
#  HELPER FUNCTIONS
# ==========================
def normalize(s):
    """Normalize string for matching"""
    if s is None: return ""
    s = str(s).lower().strip()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def split_parts(csv_value):
    """Split CSV value by common delimiters"""
    if csv_value is None: return []
    parts = re.split(r"[;,/|]", str(csv_value))
    return [normalize(p) for p in parts if p.strip()]

def matches(user_input, csv_value):
    """Check if user input matches CSV value"""
    ui = normalize(user_input)
    if ui == "": return True
    for p in split_parts(csv_value):
        if ui == p or ui in p or p in ui:
            return True
    return False

# Initialize users dictionary
USERS = load_users()
