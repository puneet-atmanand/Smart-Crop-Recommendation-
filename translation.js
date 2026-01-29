// Translation System
// Language switching and UI translation functionality

// Language switching
async function switchLanguage(lang) {
    if (lang === currentLang || isTranslating) return;

    currentLang = lang;
    sessionStorage.setItem("lang", lang);

    await applyTranslations(lang);
    await loadOptions(); // Reload options in new language
}

// Translation system
async function applyTranslations(lang) {
    console.log(`Applying translations for language: ${lang}`);

    if (isTranslating) {
        console.log("Translation already in progress, skipping...");
        return;
    }

    try {
        isTranslating = true;

        if (lang === "en") {
            resetToEnglish();
            translatedTexts = {};
            return;
        }

        const res = await safeFetch(API + "/translate_ui", {
            method: "POST",
            body: JSON.stringify({ lang, username: sessionStorage.getItem("username") })
        }, 1);

        if (!res.ok) {
            console.warn("Translation service unavailable, using English");
            resetToEnglish();
            return;
        }

        const texts = await res.json();
        if (texts.error) {
            console.warn("Translation failed:", texts.error);
            if (texts.fallback) {
                translatedTexts = texts.fallback;
                resetToEnglish();
            }
            return;
        }

        translatedTexts = texts;
        updateAllUIElements(texts);

        console.log(`Translation completed for language: ${lang}`);

    } catch (err) {
        console.error("Translation error:", err);
        resetToEnglish();
    } finally {
        isTranslating = false;
    }
}

// Update UI elements with translations
function updateAllUIElements(texts) {
    // Main UI elements
    const elements = {
        "page-title": texts.title || "Smart Crop Recommendation",
        "login-header": texts.login_header || "Farmer Login",
        "register-header": texts.register_header || "Register",
        "login-btn": texts.login_btn || "Login",
        "register-btn": texts.register_btn || "Register",
        "recommend-btn": texts.get_recommendation || "Get Recommendation",
        "yield-btn": texts.predict_yield || "Predict Yield",
        "logout-btn": texts.logout || "Logout",
        "footer": texts.footer || "PROJECT BY TEAM BELLATOR ARIETES",
        "new-here-text": (texts.new_here || "New here?") + " " + `<a href="#" onclick="showRegister()" style="color: #81c784;">${texts.register_link || "Register"}</a>`,
        "already-text": (texts.already_have || "Already have an account?") + " " + `<a href="#" onclick="showLogin()" style="color: #81c784;">${texts.login_link || "Login"}</a>`,
        "lang-label": texts.change_language || "Change Language:"
    };

    for (const [id, text] of Object.entries(elements)) {
        const element = document.getElementById(id);
        if (element && text) {
            if (id === "new-here-text" || id === "already-text") {
                element.innerHTML = text;
            } else {
                element.innerText = text;
            }
        }
    }

    // Tab labels
    const recommendationTab = document.getElementById("recommendation-tab");
    const yieldTab = document.getElementById("yield-tab");
    const userinfoTab = document.getElementById("userinfo-tab");

    if (recommendationTab) {
        recommendationTab.innerText = texts.crop_recommendation_tab || "Crop Recommendation";
    }
    if (yieldTab) {
        yieldTab.innerText = texts.yield_prediction_tab || "Yield Prediction";
    }
    if (userinfoTab) {
        userinfoTab.innerText = texts.user_info_tab || "User Info";
    }

    // Form labels
    const formLabels = {
        "label-seed": texts.seed || "Seed/Crop:",
        "label-soil": texts.soil || "Soil Type:",
        "label-season": texts.season || "Season:",
        "label-location": texts.location || "Location/State:",
        "label-yield-seed": texts.select_crop_label || "Select Crop:",
        "label-soil-temp": texts.soil_temperature_label || "Soil Temperature (°C):",
        "label-ph": texts.ph_level || "Soil pH:",
        "label-rainfall": texts.rainfall || "Rainfall (mm):",
        "recommendation-subtitle": texts.get_personalized || "Get personalized crop recommendations based on your conditions",
        "yield-subtitle": texts.predict_crop_yield || "Predict crop yield based on environmental conditions"
    };

    for (const [id, text] of Object.entries(formLabels)) {
        const element = document.getElementById(id);
        if (element && text) {
            element.innerText = text;
        }
    }

    // User Info Tab Elements
    const userInfoElements = {
        "profile-title": texts.profile || "Profile",
        "about-title": texts.about_us || "About Us",
        "contact-title": texts.contact_us || "Contact Us",
        "help-title": texts.help || "Help",
        "feedback-title": texts.feedback || "Feedback",
        "about-description": texts.about_description || "Smart Crop Recommendation System helps farmers make informed decisions about crop selection based on soil conditions, climate, and local factors. Our advanced algorithms analyze multiple parameters to provide personalized recommendations.",
        "contact-email": texts.contact_email || "Email: support@croprecosystem.com",
        "contact-phone": texts.contact_phone || "Phone: +91-9876543210",
        "contact-address": texts.contact_address || "Address: Agricultural Technology Center, Bengaluru, Karnataka, India",
        "help-how-to-use": texts.help_how_to_use || "How to Use",
        "help-step1": texts.help_step1 || "1. Login with your credentials or register as a new user",
        "help-step2": texts.help_step2 || "2. Select your preferred language from the dropdown",
        "help-step3": texts.help_step3 || "3. Use Crop Recommendation tab to get suggestions based on your conditions",
        "help-step4": texts.help_step4 || "4. Use Yield Prediction tab to estimate expected crop yield",
        "help-faq": texts.help_faq || "Frequently Asked Questions",
        "help-faq1": texts.help_faq1 || "Q: How accurate are the recommendations?",
        "help-faq1-ans": texts.help_faq1_ans || "A: Our system uses comprehensive agricultural databases and considers multiple factors for high accuracy.",
        "help-faq2": texts.help_faq2 || "Q: Can I use this system offline?",
        "help-faq2-ans": texts.help_faq2_ans || "A: Currently, the system requires internet connection for translation and database access.",
        "feedback-rating-label": texts.feedback_rating || "Rate your experience (1-5 stars):",
        "feedback-comments-label": texts.feedback_comments || "Your feedback and suggestions:",
        "submit-feedback-btn": texts.submit_feedback || "Submit Feedback"
    };

    for (const [id, text] of Object.entries(userInfoElements)) {
        const element = document.getElementById(id);
        if (element && text) {
            element.innerText = text;
        }
    }
}

// Reset to English
function resetToEnglish() {
    const englishTexts = {
        "page-title": "Smart Crop Recommendation",
        "login-header": "Farmer Login",
        "register-header": "Register",
        "login-btn": "Login",
        "register-btn": "Register",
        "recommend-btn": "Get Recommendation",
        "yield-btn": "Predict Yield",
        "logout-btn": "Logout",
        "footer": "PROJECT BY TEAM BELLATOR ARIETES",
        "new-here-text": `New here? <a href="#" onclick="showRegister()" style="color: #81c784;">Register</a>`,
        "already-text": `Already have an account? <a href="#" onclick="showLogin()" style="color: #81c784;">Login</a>`,
        "lang-label": "Change Language:",
        "label-seed": "Seed/Crop:",
        "label-soil": "Soil Type:",
        "label-season": "Season:",
        "label-location": "Location/State:",
        "label-yield-seed": "Select Crop:",
        "label-soil-temp": "Soil Temperature (°C):",
        "label-ph": "Soil pH:",
        "label-rainfall": "Rainfall (mm):",
        "recommendation-subtitle": "Get personalized crop recommendations based on your conditions",
        "yield-subtitle": "Predict crop yield based on environmental conditions",
        "profile-title": "Profile",
        "about-title": "About Us",
        "contact-title": "Contact Us",
        "help-title": "Help",
        "feedback-title": "Feedback"
    };

    // Set tab labels
    const recommendationTab = document.getElementById("recommendation-tab");
    const yieldTab = document.getElementById("yield-tab");
    const userinfoTab = document.getElementById("userinfo-tab");

    if (recommendationTab) recommendationTab.innerText = "Crop Recommendation";
    if (yieldTab) yieldTab.innerText = "Yield Prediction";
    if (userinfoTab) userinfoTab.innerText = "User Info";

    // Apply English texts
    for (const [id, text] of Object.entries(englishTexts)) {
        const element = document.getElementById(id);
        if (element && text) {
            if (id === "new-here-text" || id === "already-text") {
                element.innerHTML = text;
            } else {
                element.innerText = text;
            }
        }
    }
}
