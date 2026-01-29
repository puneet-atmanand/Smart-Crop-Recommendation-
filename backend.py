"""
Smart Crop Recommendation System - Main Entry Point
Simplified backend that imports and orchestrates all modules
"""

from flask import Flask
from flask_cors import CORS
import os

# Import configuration
from config import BASE_DIR, CSV_FN, USERS_FILE, FEEDBACK_FILE, VALID_LANGS
from database import df, USERS
from translation import translator, translation_cache
from yield_prediction import get_yield_crops
from routes import register_routes

# ==========================
#  FLASK APP SETUP
# ==========================
app = Flask(__name__)
CORS(app, origins=["*"])

# Register all routes
register_routes(app)

# ==========================
#  RUN APP
# ==========================
if __name__ == "__main__":
    print("="*60)
    print("SMART CROP RECOMMENDATION SYSTEM - ENHANCED WITH USER INFO")
    print("="*60)
    print("Starting server with enhanced translation support & user management...")
    print(f"Server URL: http://127.0.0.1:5000")
    print(f"Base Directory: {BASE_DIR}")
    print(f"Index file: {os.path.join(BASE_DIR, 'index.html')}")
    print(f"Crops database: {CSV_FN}")
    print(f"Users database: {USERS_FILE}")
    print(f"Feedback database: {FEEDBACK_FILE}")
    print(f"Yield prediction crops: {len(get_yield_crops())} available")
    print(f"Translation system: {'Active' if translator else 'Inactive'}")
    print(f"Translation cache: Ready (0 entries)")
    print(f"Registered users: {len(USERS)}")
    print("="*60)
    
    # Check if required files exist
    files_status = []
    if os.path.exists(os.path.join(BASE_DIR, "index.html")):
        files_status.append("index.html found")
    else:
        files_status.append("index.html NOT FOUND - Place your HTML file in the same directory")
        
    if os.path.exists(CSV_FN):
        files_status.append(f"crops.csv found ({len(df)} crops loaded)")
    else:
        files_status.append("crops.csv created with sample data")
        
    for status in files_status:
        print(status)
    
    print("="*60)
    print("Enhanced API Endpoints:")
    print("  GET  /health                  - Server health check & status")
    print("  GET  /                        - Main application")
    print("  POST /login                   - User authentication with session tracking")
    print("  POST /logout                  - Proper user logout with session cleanup")
    print("  POST /register                - New user registration with timestamps")
    print("  GET  /get_options             - Get crop options (with translation)")
    print("  POST /get_related_options     - Get filtered options (with translation)")
    print("  POST /get_crop_info           - Get crop recommendation (with translation)")
    print("  POST /predict_yield           - Predict crop yield (with translation)")
    print("  POST /translate_ui            - Translate UI elements")
    print("  POST /submit_feedback         - Submit user feedback")
    print("  POST /get_user_profile        - Get user profile information")
    print("  POST /clear_translation_cache - Clear translation cache")
    print("="*60)
    print("Features:")
    print("  - Multi-language support (11+ Indian languages)")
    print("  - Enhanced yield prediction algorithm")
    print("  - User session management")
    print("  - Feedback system")
    print("  - Translation caching for performance")
    print("  - Comprehensive error handling")
    print("  - Session activity tracking")
    print("="*60)
    
    app.run(debug=True, host="0.0.0.0", port=5000)
