import sys
import traceback

try:
    print("Testing imports...")
    from flask import Flask
    from flask_cors import CORS
    print("✓ Flask imports successful")
    
    from config import BASE_DIR, CSV_FN, USERS_FILE, FEEDBACK_FILE, VALID_LANGS
    print("✓ config import successful")
    
    from database import df, USERS
    print(f"✓ database import successful - {len(df)} rows loaded")
    
    from translation import translator, translation_cache
    print("✓ translation import successful")
    
    from yield_prediction import get_yield_crops
    print(f"✓ yield_prediction import successful - {len(get_yield_crops())} crops")
    
    from routes import register_routes
    print("✓ routes import successful")
    
    print("\nCreating Flask app...")
    app = Flask(__name__)
    CORS(app, origins=["*"])
    print("✓ Flask app created")
    
    print("\nRegistering routes...")
    register_routes(app)
    print("✓ Routes registered")
    
    print("\nStarting server...")
    app.run(debug=True, host="0.0.0.0", port=5000)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
