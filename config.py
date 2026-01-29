"""
Configuration and Constants
Centralized configuration for the Smart Crop Recommendation System
"""

import os
import logging

# ==========================
#  LOGGING CONFIGURATION
# ==========================
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ==========================
#  FILE PATHS
# ==========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FN = os.path.join(BASE_DIR, "crops.csv")
USERS_FILE = os.path.join(BASE_DIR, "users.csv")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.csv")

# ==========================
#  TRANSLATION CACHE
# ==========================
translation_cache = {}  # Cache for translations to improve performance

# ==========================
#  UI TRANSLATIONS
# ==========================
# Comprehensive UI text dictionary for all supported languages
UI_TRANSLATIONS = {
    "en": {
        "title": "Smart Crop Recommendation",
        "login_header": "Farmer Login",
        "register_header": "Register",
        "username": "Username",
        "password": "Password",
        "login_btn": "Login",
        "register_btn": "Register",
        "seed": "Seed/Crop",
        "soil": "Soil Type",
        "season": "Season",
        "location": "Location/State",
        "get_recommendation": "Get Recommendation",
        "predict_yield": "Predict Yield",
        "logout": "Logout",
        "footer": "PROJECT BY TEAM BELLATOR ARIETES",
        "new_here": "New here?",
        "already_have": "Already have an account?",
        "register_link": "Register",
        "login_link": "Login",
        "crop_recommendation_tab": "Crop Recommendation",
        "yield_prediction_tab": "Yield Prediction",
        "user_info_tab": "User Info",
        "change_language": "Change Language",
        "select_option": "-- Select --",
        "fill_all_fields": "Please fill in all fields",
        "fetching_recommendation": "Fetching recommendation...",
        "no_match_found": "No match found",
        "connection_error": "Error connecting to backend. Please check server status.",
        "temp_validation": "Please provide a valid soil temperature between 1-50°C",
        "ph_validation": "Please provide a valid pH value between 1-14",
        "rainfall_validation": "Please provide a valid rainfall amount (0-5000mm)",
        "select_crop_first": "Please select a crop first to predict yield",
        "analyzing_conditions": "Analyzing environmental conditions and predicting yield...",
        "prediction_failed": "Prediction failed",
        "predicted_yield_for": "Predicted Yield for",
        "quality_label": "Quality",
        "confidence_score": "Confidence Score",
        "temp_score": "Temperature Score",
        "ph_score": "pH Score",
        "rain_score": "Rainfall Score",
        "input_label": "Input",
        "optimal_conditions": "Optimal Conditions for",
        "temperature": "Temperature",
        "ph_level": "pH Level",
        "rainfall": "Rainfall",
        "yield_range_analysis": "Yield Range Analysis",
        "min_expected": "Minimum Expected",
        "your_prediction": "Your Prediction",
        "max_possible": "Maximum Possible",
        "agri_recommendations": "Agricultural Recommendations",
        "algorithm": "Algorithm",
        "algorithm_desc": "Advanced multi-factor prediction considering temperature optimization, pH balance, rainfall adequacy, and crop-specific characteristics from a comprehensive agricultural database.",
        "info_label": "Information",
        "growth_days_label": "Growth Days",
        "fertilizers_label": "Fertilizers",
        "irrigation_label": "Irrigation",
        "get_personalized": "Get personalized crop recommendations based on your conditions",
        "predict_crop_yield": "Predict crop yield based on environmental conditions",
        "are_you_sure_logout": "Are you sure you want to logout?",
        "soil_temperature_label": "Soil Temperature (°C)",
        "select_crop_label": "Select Crop",
        "enter_temp_placeholder": "Enter soil temperature (e.g., 25.5)",
        "enter_ph_placeholder": "Enter soil pH (e.g., 6.5)",
        "enter_rainfall_placeholder": "Enter rainfall (e.g., 1200)",
        
        # User Info Tab Translations
        "about_us": "About Us",
        "contact_us": "Contact Us", 
        "help": "Help",
        "feedback": "Feedback",
        "profile": "Profile",
        "about_description": "Smart Crop Recommendation System helps farmers make informed decisions about crop selection based on soil conditions, climate, and local factors. Our advanced algorithms analyze multiple parameters to provide personalized recommendations.",
        "contact_email": "Email: bellatorarietes@gmail.com",
        "contact_phone": "Phone: +91-7483290488",
        "contact_address": "Address: MIT Agricultural Technology Center,Mysore, Karnataka, India",
        "help_how_to_use": "How to Use",
        "help_step1": "1. Login with your credentials or register as a new user",
        "help_step2": "2. Select your preferred language from the dropdown",
        "help_step3": "3. Use Crop Recommendation tab to get suggestions based on your conditions",
        "help_step4": "4. Use Yield Prediction tab to estimate expected crop yield",
        "help_faq": "Frequently Asked Questions",
        "help_faq1": "Q: How accurate are the recommendations?",
        "help_faq1_ans": "A: Our system uses comprehensive agricultural databases and considers multiple factors for high accuracy.",
        "help_faq2": "Q: Can I use this system offline?",
        "help_faq2_ans": "A: Currently, the system requires internet connection for translation and database access.",
        "feedback_rating": "Rate your experience (1-5 stars)",
        "feedback_comments": "Your feedback and suggestions",
        "submit_feedback": "Submit Feedback",
        "feedback_success": "Thank you for your feedback!",
        "feedback_error": "Failed to submit feedback. Please try again.",
        "profile_info": "Profile Information",
        "profile_username": "Username",
        "profile_language": "Preferred Language",
        "profile_member_since": "Member Since",
        "profile_last_login": "Last Login",
        "logout_success": "Logged out successfully"
    }
}

# ==========================
#  SUPPORTED LANGUAGES
# ==========================
VALID_LANGS = ['en', 'hi', 'ta', 'te', 'kn', 'ml', 'bn', 'gu', 'mr', 'pa', 'ur']
