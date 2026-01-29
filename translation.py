"""
Translation System
Manages all translation-related functionality including caching and batch translation
"""

import logging
import time
from googletrans import Translator
from config import translation_cache, UI_TRANSLATIONS

# ==========================
#  TRANSLATOR INITIALIZATION
# ==========================
translator = None

def init_translator():
    """Initialize Google Translator with error handling"""
    global translator
    try:
        translator = Translator()
        # Test with a simple translation
        test_result = translator.translate("Hello", dest="hi")
        if test_result and hasattr(test_result, 'text'):
            logging.info("✅ Google Translator initialized successfully")
            return True
        else:
            logging.warning("⚠ Translator test failed, translation may not work properly")
            return False
    except Exception as e:
        logging.error(f"❌ Failed to initialize translator: {e}")
        translator = None
        return False

# Try to initialize translator
init_translator()

# ==========================
#  TRANSLATION FUNCTIONS
# ==========================
def get_cache_key(text, target_lang):
    """Generate cache key for translation"""
    return f"{text[:50]}_{target_lang}"

def translate_text_enhanced(text, target_lang, max_retries=3):
    """Enhanced translation with caching and retry logic"""
    if not text or target_lang == "en" or target_lang is None:
        return text
    
    # Check cache first
    cache_key = get_cache_key(text, target_lang)
    if cache_key in translation_cache:
        return translation_cache[cache_key]
    
    # Check if translator is available
    if not translator:
        logging.warning("⚠ Translator not available, attempting to reinitialize...")
        if not init_translator():
            return text
    
    # Skip translation for very short text, numbers, or special characters
    if len(str(text).strip()) < 2 or str(text).replace(' ', '').replace('-', '').isdigit():
        return text
    
    try:
        for attempt in range(max_retries):
            try:
                result = translator.translate(text, dest=target_lang)
                if result and hasattr(result, 'text') and result.text:
                    translated_text = result.text
                    # Cache the result
                    translation_cache[cache_key] = translated_text
                    logging.debug(f"✅ Translated '{text}' to '{target_lang}': '{translated_text}'")
                    return translated_text
                else:
                    raise Exception("Empty translation result")
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                logging.warning(f"Translation attempt {attempt + 1} failed, retrying...")
                time.sleep(0.5)  # Brief delay before retry
        
    except Exception as e:
        logging.error(f"❌ Translation failed for '{text}' to '{target_lang}' after {max_retries} attempts: {e}")
        return text

def back_translate_enhanced(value, src_lang, max_retries=3):
    """Enhanced back-translation with caching"""
    if not value or src_lang == "en" or src_lang is None:
        return value
    
    # Check cache first
    cache_key = get_cache_key(f"back_{value}", src_lang)
    if cache_key in translation_cache:
        return translation_cache[cache_key]
    
    if not translator:
        logging.warning("⚠ Translator not available for back-translation")
        return value
        
    if len(str(value).strip()) < 2 or str(value).replace(' ', '').replace('-', '').isdigit():
        return value
        
    try:
        for attempt in range(max_retries):
            try:
                result = translator.translate(value, dest="en", src=src_lang)
                if result and hasattr(result, 'text') and result.text:
                    back_translated = result.text
                    # Cache the result
                    translation_cache[cache_key] = back_translated
                    logging.debug(f"✅ Back-translated '{value}' from '{src_lang}': '{back_translated}'")
                    return back_translated
                else:
                    raise Exception("Empty back-translation result")
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                logging.warning(f"Back-translation attempt {attempt + 1} failed, retrying...")
                time.sleep(0.5)
        
    except Exception as e:
        logging.error(f"❌ Back-translation failed for '{value}' from '{src_lang}' after {max_retries} attempts: {e}")
        return value

def get_ui_translation(lang_code, key, fallback_text=None):
    """Get UI translation for specific key and language"""
    if lang_code == "en":
        return UI_TRANSLATIONS["en"].get(key, fallback_text or key)
    
    # If translation not in cache, translate on demand
    english_text = UI_TRANSLATIONS["en"].get(key, fallback_text or key)
    return translate_text_enhanced(english_text, lang_code)

def batch_translate_ui(lang_code):
    """Batch translate all UI elements for a language"""
    if lang_code == "en":
        return UI_TRANSLATIONS["en"]
    
    translated_ui = {}
    english_ui = UI_TRANSLATIONS["en"]
    
    for key, english_text in english_ui.items():
        translated_ui[key] = translate_text_enhanced(english_text, lang_code)
    
    return translated_ui

def cleanup_translation_cache():
    """Clean up old translation cache entries periodically"""
    global translation_cache
    # Keep only the most recent 1000 translations
    if len(translation_cache) > 1000:
        # Keep the last 500 entries (simple cleanup strategy)
        items = list(translation_cache.items())
        translation_cache = dict(items[-500:])
        logging.info(f"🧹 Translation cache cleaned up, kept 500 most recent entries")
