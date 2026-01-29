"""
Flask Routes
All API endpoint handlers for the Smart Crop Recommendation System
"""

from flask import request, jsonify, send_from_directory, abort
import logging
import time
import uuid
import re
import traceback

from config import BASE_DIR, VALID_LANGS, translation_cache
from database import df, USERS, save_users, save_feedback, matches
from translation import (
    translator, translate_text_enhanced, back_translate_enhanced,
    get_ui_translation, batch_translate_ui
)
from auth import ACTIVE_SESSIONS, update_user_activity, cleanup_inactive_sessions
from yield_prediction import calculate_yield_prediction, get_yield_crops

def register_routes(app):
    """Register all routes with the Flask app"""
    
    # ==========================
    #  HEALTH CHECK
    # ==========================
    @app.route("/health", methods=["GET"])
    def health_check():
        cleanup_inactive_sessions()  # Clean up inactive sessions
        return jsonify({
            "status": "OK", 
            "message": "Server is running",
            "crops_loaded": len(df),
            "users_registered": len(USERS),
            "active_sessions": len(ACTIVE_SESSIONS),
            "yield_crops_available": len(get_yield_crops()),
            "translation_cache_size": len(translation_cache),
            "translator_status": "available" if translator else "unavailable",
            "endpoints_available": [
                "/health", "/", "/login", "/logout", "/register", "/get_options", 
                "/get_related_options", "/get_crop_info", "/predict_yield", "/translate_ui",
                "/submit_feedback", "/get_user_profile"
            ]
        }), 200

    # ==========================
    #  AUTHENTICATION ROUTES
    # ==========================
    @app.route("/login", methods=["POST"])
    def login():
        try:
            data = request.get_json(force=True)
            username = data.get("username", "").lower().strip()
            password = data.get("password", "").strip()

            if not username or not password:
                return jsonify({"error": "Username and password required"}), 400

            user = USERS.get(username)
            if not user or user["password"] != password:
                return jsonify({"error": "Invalid credentials"}), 401

            # Update login tracking
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            USERS[username]["last_login"] = current_time
            save_users(USERS)
            
            # Create active session
            session_id = str(uuid.uuid4())
            ACTIVE_SESSIONS[username] = {
                "login_time": time.time(),
                "last_activity": time.time(),
                "session_id": session_id
            }

            logging.info(f"✅ User logged in: {username} (language: {user['lang']})")
            return jsonify({
                "message": "Login successful", 
                "lang": user["lang"],
                "session_id": session_id,
                "username": username
            })
        except Exception as e:
            logging.error(f"Login error: {e}")
            return jsonify({"error": "Login failed"}), 500

    @app.route("/logout", methods=["POST"])
    def logout():
        try:
            data = request.get_json(force=False) or {}
            username = data.get("username", "").lower().strip()
            session_id = data.get("session_id", "")
            
            # Remove from active sessions
            if username in ACTIVE_SESSIONS:
                stored_session = ACTIVE_SESSIONS[username]
                if not session_id or stored_session.get("session_id") == session_id:
                    del ACTIVE_SESSIONS[username]
                    logging.info(f"✅ User logged out: {username}")
                    return jsonify({"message": "Logged out successfully"})
                else:
                    return jsonify({"error": "Invalid session"}), 400
            else:
                # User might already be logged out or session expired
                return jsonify({"message": "Session already ended"})
                
        except Exception as e:
            logging.error(f"Logout error: {e}")
            return jsonify({"error": "Logout failed"}), 500

    @app.route("/register", methods=["POST"])
    def register():
        try:
            data = request.get_json(force=True)
            username = data.get("username", "").lower().strip()
            password = data.get("password", "").strip()
            lang = data.get("lang", "en").lower().strip()

            # Validation
            if not username or not password:
                return jsonify({"error": "Username and password required"}), 400
            if len(username) < 3:
                return jsonify({"error": "Username must be at least 3 characters long"}), 400
            if len(password) < 4:
                return jsonify({"error": "Password must be at least 4 characters long"}), 400
            if username in USERS:
                return jsonify({"error": "User already exists"}), 400

            # Validate language code
            if lang not in VALID_LANGS:
                lang = 'en'

            # Create user with timestamps
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            USERS[username] = {
                "password": password, 
                "lang": lang,
                "created_at": current_time,
                "last_login": ""
            }
            save_users(USERS)
            logging.info(f"✅ New user registered: {username} with language: {lang}")
            return jsonify({"message": "User registered successfully", "lang": lang})
        except Exception as e:
            logging.error("register error: %s", e)
            return jsonify({"error": "Registration failed"}), 500

    # ==========================
    #  USER PROFILE & FEEDBACK
    # ==========================
    @app.route("/submit_feedback", methods=["POST"])
    def submit_feedback():
        try:
            data = request.get_json(force=True)
            username = data.get("username", "").lower().strip()
            rating = data.get("rating", 0)
            feedback_text = data.get("feedback", "").strip()
            
            if not username:
                return jsonify({"error": "Username required"}), 400
            
            if not (1 <= rating <= 5):
                return jsonify({"error": "Rating must be between 1 and 5"}), 400
                
            if len(feedback_text) > 1000:
                return jsonify({"error": "Feedback too long (max 1000 characters)"}), 400
            
            # Verify user is logged in
            if username not in ACTIVE_SESSIONS:
                return jsonify({"error": "Please login to submit feedback"}), 401
            
            # Update user activity
            update_user_activity(username)
            
            # Save feedback
            success = save_feedback(username, rating, feedback_text)
            
            if success:
                logging.info(f"✅ Feedback submitted by {username}: {rating}/5 stars")
                return jsonify({"message": "Thank you for your feedback!"})
            else:
                return jsonify({"error": "Failed to save feedback"}), 500
                
        except Exception as e:
            logging.error(f"Feedback submission error: {e}")
            return jsonify({"error": "Failed to submit feedback"}), 500

    @app.route("/get_user_profile", methods=["POST"])
    def get_user_profile():
        try:
            data = request.get_json(force=True)
            username = data.get("username", "").lower().strip()
            
            if not username:
                return jsonify({"error": "Username required"}), 400
            
            # Verify user is logged in
            if username not in ACTIVE_SESSIONS:
                return jsonify({"error": "Please login to view profile"}), 401
            
            # Update user activity
            update_user_activity(username)
            
            user_data = USERS.get(username)
            if not user_data:
                return jsonify({"error": "User not found"}), 404
            
            # Return profile information (exclude password)
            profile = {
                "username": username,
                "language": user_data.get("lang", "en"),
                "created_at": user_data.get("created_at", "Unknown"),
                "last_login": user_data.get("last_login", "Never")
            }
            
            return jsonify(profile)
            
        except Exception as e:
            logging.error(f"Get user profile error: {e}")
            return jsonify({"error": "Failed to get user profile"}), 500

    # ==========================
    #  CROP OPTIONS
    # ==========================
    @app.route("/get_options", methods=["GET"])
    def get_options():
        try:
            lang = request.args.get("lang", "en") or "en"
            tab = request.args.get("tab", "recommendation") or "recommendation"

            # Get unique values for different tabs
            if tab == "yield":
                # For yield prediction, return crops from the yield database
                yield_crops = get_yield_crops()
                seed_options = yield_crops
            else:
                # For recommendation, use the CSV data
                seed_options = []
                if 'seed' in df.columns:
                    for val in df['seed'].dropna().unique():
                        for part in re.split(r"[;,/|]", str(val)):
                            if part.strip():
                                seed_options.append(part.strip())
                    seed_options = sorted(set(seed_options))

            def get_unique_values(column):
                values = []
                if column in df.columns:
                    for val in df[column].dropna().unique():
                        for part in re.split(r"[;,/|]", str(val)):
                            if part.strip():
                                values.append(part.strip())
                return sorted(set(values))

            soil_options = get_unique_values('soil')
            season_options = get_unique_values('season')
            states_options = get_unique_values('states')

            # Translate if needed
            if lang and lang != "en":
                seed_options = [translate_text_enhanced(v, lang) for v in seed_options]
                soil_options = [translate_text_enhanced(v, lang) for v in soil_options]
                season_options = [translate_text_enhanced(v, lang) for v in season_options]
                states_options = [translate_text_enhanced(v, lang) for v in states_options]

            return jsonify({
                "seed": seed_options,
                "soil": soil_options,
                "season": season_options,
                "states": states_options
            })
        except Exception as e:
            logging.error("get_options error: %s", e)
            return jsonify({"error": "Failed to get options"}), 500

    @app.route("/get_related_options", methods=["POST"])
    def get_related_options():
        try:
            data = request.get_json(force=True) or {}
            seed = data.get("seed", "")
            lang = data.get("lang", "en") or "en"
            username = data.get("username", "")

            # Update user activity if logged in
            if username and username.lower() in ACTIVE_SESSIONS:
                update_user_activity(username.lower())

            if not seed:
                return jsonify({"soil": [], "season": [], "states": []})

            # Back-translate to English for matching
            seed_en = back_translate_enhanced(seed, lang)

            # Find crops that match the selected seed
            subset = df[df.apply(lambda row: matches(seed_en, row.get("seed", "")), axis=1)]
            
            def get_unique_values(col):
                if col in subset.columns and not subset.empty:
                    values = []
                    for v in subset[col].dropna().unique():
                        for part in re.split(r"[;,/|]", str(v)):
                            if part.strip():
                                values.append(part.strip())
                    return sorted(set(values))
                return []
            
            soils = get_unique_values("soil")
            seasons = get_unique_values("season")
            states = get_unique_values("states")

            # Translate if needed
            if lang and lang != "en":
                soils = [translate_text_enhanced(v, lang) for v in soils]
                seasons = [translate_text_enhanced(v, lang) for v in seasons]
                states = [translate_text_enhanced(v, lang) for v in states]

            logging.info(f"✅ Related options loaded for seed: {seed} (language: {lang})")
            return jsonify({"soil": soils, "season": seasons, "states": states})
        except Exception as e:
            logging.error("get_related_options error: %s", e)
            return jsonify({"error": "Failed to get related options"}), 500

    # ==========================
    #  CROP RECOMMENDATION
    # ==========================
    @app.route("/get_crop_info", methods=["POST"])
    def get_crop_info():
        try:
            data = request.get_json(force=True, silent=True) or {}
            seed = data.get("seed", "").strip()
            soil = data.get("soil", "").strip()
            season = data.get("season", "").strip()
            location = data.get("location", "").strip()
            lang = data.get("lang", "en") or "en"
            username = data.get("username", "")

            # Update user activity if logged in
            if username and username.lower() in ACTIVE_SESSIONS:
                update_user_activity(username.lower())

            if not all([seed, soil, season, location]):
                error_msg = get_ui_translation(lang, "fill_all_fields", "All fields (seed, soil, season, location) are required")
                return jsonify({"error": error_msg}), 400

            # Back-translate to English for matching
            seed_en = back_translate_enhanced(seed, lang)
            soil_en = back_translate_enhanced(soil, lang)
            season_en = back_translate_enhanced(season, lang)
            location_en = back_translate_enhanced(location, lang)

            # Find matching crops with fuzzy matching
            matched = df[df.apply(lambda row: (
                matches(seed_en, row.get("seed","")) and
                matches(soil_en, row.get("soil","")) and
                matches(season_en, row.get("season","")) and
                matches(location_en, row.get("states",""))
            ), axis=1)]

            if matched.empty:
                # Try partial matching if exact match fails
                partial_matched = df[df.apply(lambda row: (
                    matches(seed_en, row.get("seed",""))
                ), axis=1)]
                
                if not partial_matched.empty:
                    matched = partial_matched.head(1)
                    logging.info(f"⚠ Using partial match for {seed_en}")
                else:
                    error_msg = get_ui_translation(lang, "no_match_found", "No matching crop found for the given conditions. Please try different parameters.")
                    return jsonify({"error": error_msg}), 404

            row0 = matched.iloc[0].to_dict()
            result = {
                "seed": row0.get("seed", ""),
                "info": row0.get("info", ""),
                "growth_days": row0.get("growth_days", ""),
                "fertilizers": row0.get("fertilizers", ""),
                "irrigation": row0.get("irrigation", "")
            }

            # Translate results if needed
            if lang and lang != "en":
                for k in result:
                    if result[k]:
                        result[k] = translate_text_enhanced(result[k], lang)

            logging.info(f"✅ Crop info found: {result['seed']} for user query in {lang}")
            return jsonify(result)
        except Exception as e:
            logging.error("get_crop_info exception:\n" + traceback.format_exc())
            return jsonify({"error": "Internal server error"}), 500

    # ==========================
    #  YIELD PREDICTION
    # ==========================
    @app.route("/predict_yield", methods=["POST"])
    def predict_yield():
        try:
            data = request.get_json(force=True) or {}
            soil_temp = float(data.get("soil_temp", 0))
            ph = float(data.get("ph", 0))
            rainfall = float(data.get("rainfall", 0))
            selected_crop = data.get("selected_crop", "").strip()
            lang = data.get("lang", "en") or "en"
            username = data.get("username", "")

            # Update user activity if logged in
            if username and username.lower() in ACTIVE_SESSIONS:
                update_user_activity(username.lower())

            # Enhanced input validation with translated messages
            if soil_temp <= 0 or soil_temp > 50:
                error_msg = get_ui_translation(lang, "temp_validation", "Please provide a valid soil temperature between 1-50°C")
                return jsonify({"error": error_msg}), 400
            if ph <= 0 or ph > 14:
                error_msg = get_ui_translation(lang, "ph_validation", "Please provide a valid pH value between 1-14")
                return jsonify({"error": error_msg}), 400
            if rainfall < 0 or rainfall > 5000:
                error_msg = get_ui_translation(lang, "rainfall_validation", "Please provide a valid rainfall amount (0-5000mm)")
                return jsonify({"error": error_msg}), 400
            if not selected_crop:
                error_msg = get_ui_translation(lang, "select_crop_first", "Please select a crop first to predict yield")
                return jsonify({"error": error_msg}), 400

            # Back-translate crop name if needed
            selected_crop_en = back_translate_enhanced(selected_crop, lang)

            # Use enhanced yield prediction algorithm
            overall_score, factors = calculate_yield_prediction(soil_temp, ph, rainfall, selected_crop_en)
            
            # Get crop data from the comprehensive database
            crop_data = factors['crop_data']
            
            # Calculate final yield with realistic algorithm
            min_yield = crop_data["base"] * 0.3  # Minimum possible yield (30% of base)
            max_yield = crop_data["max"]          # Maximum possible yield
            
            predicted_yield = min_yield + (max_yield - min_yield) * overall_score
            predicted_yield = round(predicted_yield, 2)

            # Determine yield quality based on score
            if overall_score >= 0.85:
                quality = "Excellent"
                quality_color = "#4caf50"
            elif overall_score >= 0.65:
                quality = "Good" 
                quality_color = "#8bc34a"
            elif overall_score >= 0.45:
                quality = "Average"
                quality_color = "#ff9800"
            elif overall_score >= 0.25:
                quality = "Below Average"
                quality_color = "#ff5722"
            else:
                quality = "Poor"
                quality_color = "#f44336"

            # Translate crop name and quality if needed
            crop_display = translate_text_enhanced(selected_crop, lang) if lang != "en" else selected_crop
            quality_display = translate_text_enhanced(quality, lang) if lang != "en" else quality

            # Enhanced recommendations based on environmental factors
            recommendations = []
            
            if factors['temp_factor'] < 0.6:
                if soil_temp < factors['optimal_temp'][0]:
                    rec = "Consider using mulching or greenhouse cultivation to increase temperature"
                    recommendations.append(translate_text_enhanced(rec, lang) if lang != "en" else rec)
                else:
                    rec = "Temperature is too high, consider shade nets or cooler season planting"
                    recommendations.append(translate_text_enhanced(rec, lang) if lang != "en" else rec)
            
            if factors['ph_factor'] < 0.6:
                if ph < 6.0:
                    rec = "Soil is too acidic, apply lime to increase pH"
                    recommendations.append(translate_text_enhanced(rec, lang) if lang != "en" else rec)
                else:
                    rec = "Soil is too alkaline, apply organic matter or sulfur to reduce pH"
                    recommendations.append(translate_text_enhanced(rec, lang) if lang != "en" else rec)
            
            if factors['rain_factor'] < 0.6:
                if rainfall < factors['optimal_rain']:
                    rec = "Insufficient rainfall, plan for supplemental irrigation"
                    recommendations.append(translate_text_enhanced(rec, lang) if lang != "en" else rec)
                else:
                    rec = "Excess rainfall risk, ensure proper drainage systems"
                    recommendations.append(translate_text_enhanced(rec, lang) if lang != "en" else rec)

            # Add fertilizer recommendations based on crop and conditions
            if overall_score < 0.7:
                rec = f"Consider applying balanced NPK fertilizer for {selected_crop_en} to improve yield"
                recommendations.append(translate_text_enhanced(rec, lang) if lang != "en" else rec)

            result = {
                "predicted_yield": predicted_yield,
                "units": "tons/hectare",
                "crop": crop_display,
                "quality": quality_display,
                "quality_color": quality_color,
                "confidence_score": round(overall_score * 100, 1),
                "factors": {
                    "soil_temperature": soil_temp,
                    "ph_level": ph,
                    "rainfall": rainfall,
                    "temp_score": round(factors['temp_factor'] * 100, 1),
                    "ph_score": round(factors['ph_factor'] * 100, 1),
                    "rain_score": round(factors['rain_factor'] * 100, 1)
                },
                "yield_range": {
                    "minimum": round(crop_data["base"] * 0.3, 2),
                    "maximum": crop_data["max"],
                    "base_yield": crop_data["base"]
                },
                "optimal_conditions": {
                    "temperature_range": f"{factors['optimal_temp'][0]}-{factors['optimal_temp'][1]}°C",
                    "optimal_rainfall": f"{factors['optimal_rain']}mm",
                    "ph_range": "6.0-7.5"
                },
                "recommendations": recommendations
            }

            logging.info(f"✅ Yield predicted for {selected_crop}: {predicted_yield} tons/hectare (Quality: {quality})")
            return jsonify(result)
        except ValueError as e:
            error_msg = get_ui_translation(lang, "prediction_failed", f"Invalid numeric values provided: {str(e)}")
            return jsonify({"error": error_msg}), 400
        except Exception as e:
            logging.error("predict_yield error:\n" + traceback.format_exc())
            error_msg = get_ui_translation(lang, "connection_error", "Failed to predict yield")
            return jsonify({"error": error_msg}), 500

    # ==========================
    #  TRANSLATION
    # ==========================
    @app.route("/translate_ui", methods=["POST"])
    def translate_ui():
        try:
            data = request.get_json(force=True) or {}
            lang = data.get("lang", "en") or "en"
            username = data.get("username", "")
            
            # Update user activity if logged in
            if username and username.lower() in ACTIVE_SESSIONS:
                update_user_activity(username.lower())
            
            logging.info(f"🌐 Translation requested for language: {lang}")

            # Check if this is a request for individual text translation
            individual_text = data.get("text")
            if individual_text:
                translated = translate_text_enhanced(individual_text, lang)
                return jsonify({"translated": translated})

            # Batch translate all UI elements
            translated_ui = batch_translate_ui(lang)
            
            # Add language validation
            if lang not in VALID_LANGS:
                logging.warning(f"⚠ Unsupported language code: {lang}, using English")
                from config import UI_TRANSLATIONS
                translated_ui = UI_TRANSLATIONS["en"]

            logging.info(f"✅ UI translated to {lang} with {len(translated_ui)} items")
            return jsonify(translated_ui)
            
        except Exception as e:
            logging.error(f"❌ translate_ui error: {e}")
            logging.error(traceback.format_exc())
            from config import UI_TRANSLATIONS
            return jsonify({
                "error": "Translation service failed", 
                "message": str(e),
                "fallback": UI_TRANSLATIONS["en"]  # Provide English fallback
            }), 500

    @app.route("/clear_translation_cache", methods=["POST"])
    def clear_translation_cache():
        try:
            cache_size_before = len(translation_cache)
            translation_cache.clear()
            logging.info(f"✅ Translation cache cleared: {cache_size_before} entries removed")
            return jsonify({
                "message": "Translation cache cleared successfully",
                "entries_cleared": cache_size_before
            })
        except Exception as e:
            logging.error(f"Error clearing translation cache: {e}")
            return jsonify({"error": "Failed to clear cache"}), 500

    # ==========================
    #  STATIC FILE SERVING
    # ==========================
    @app.route("/")
    def serve_index():
        try:
            import os
            index_path = os.path.join(BASE_DIR, "index.html")
            if os.path.exists(index_path):
                return send_from_directory(BASE_DIR, "index.html")
            else:
                return jsonify({
                    "error": "index.html not found",
                    "message": "Please make sure index.html is in the same directory as backend.py",
                    "current_directory": BASE_DIR,
                    "suggestion": "Create an index.html file or place your frontend files in the same directory"
                }), 404
        except Exception as e:
            logging.error(f"Error serving index: {e}")
            return jsonify({"error": "Error loading page"}), 500

    @app.route("/<path:filename>")
    def serve_static(filename):
        """Serve static files like CSS, JS, images"""
        try:
            return send_from_directory(BASE_DIR, filename)
        except Exception:
            abort(404)

    # ==========================
    #  ERROR HANDLERS
    # ==========================
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Endpoint not found",
            "available_endpoints": [
                "GET  /health - Server status",
                "GET  / - Main application",
                "POST /login - User authentication", 
                "POST /logout - User logout",
                "POST /register - User registration",
                "GET  /get_options - Get crop options",
                "POST /get_related_options - Get related options",
                "POST /get_crop_info - Get crop recommendation",
                "POST /predict_yield - Predict crop yield",
                "POST /translate_ui - Translate UI text",
                "POST /submit_feedback - Submit user feedback",
                "POST /get_user_profile - Get user profile",
                "POST /clear_translation_cache - Clear translation cache"
            ],
            "note": "Make sure you're using the correct HTTP method (GET/POST)"
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        logging.error(f"Internal server error: {error}")
        return jsonify({"error": "Internal server error", "message": "Please check server logs"}), 500

    # ==========================
    #  CORS PREFLIGHT HANDLING
    # ==========================
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "*")
            response.headers.add('Access-Control-Allow-Methods', "*")
            return response
