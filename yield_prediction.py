"""
Yield Prediction Module
Contains yield prediction algorithm and crop database
"""

from database import normalize

def get_yield_prediction_data():
    """
    Comprehensive yield prediction database with realistic values in tons per hectare
    This is separate from the crop recommendation dataset
    """
    return {
        # Cereal Crops
        "rice": {"base": 3.5, "max": 8.5, "temp_range": (25, 35), "optimal_rain": 1500},
        "wheat": {"base": 2.8, "max": 6.5, "temp_range": (15, 25), "optimal_rain": 400},
        "corn": {"base": 4.2, "max": 11.0, "temp_range": (20, 30), "optimal_rain": 600},
        "maize": {"base": 4.2, "max": 11.0, "temp_range": (20, 30), "optimal_rain": 600},
        "barley": {"base": 2.5, "max": 5.8, "temp_range": (15, 20), "optimal_rain": 300},
        "millet": {"base": 1.2, "max": 3.5, "temp_range": (25, 35), "optimal_rain": 300},
        "sorghum": {"base": 1.8, "max": 4.8, "temp_range": (25, 30), "optimal_rain": 400},
        "oats": {"base": 2.0, "max": 4.5, "temp_range": (16, 22), "optimal_rain": 350},
        
        # Oilseed Crops
        "groundnut": {"base": 1.2, "max": 4.2, "temp_range": (25, 30), "optimal_rain": 500},
        "sunflower": {"base": 1.5, "max": 3.2, "temp_range": (20, 25), "optimal_rain": 400},
        "mustard": {"base": 1.0, "max": 2.8, "temp_range": (10, 25), "optimal_rain": 300},
        "soybean": {"base": 1.8, "max": 4.0, "temp_range": (20, 30), "optimal_rain": 450},
        "sesame": {"base": 0.8, "max": 1.8, "temp_range": (25, 30), "optimal_rain": 400},
        "safflower": {"base": 1.0, "max": 2.5, "temp_range": (15, 25), "optimal_rain": 350},
        
        # Fiber Crops
        "cotton": {"base": 1.0, "max": 3.2, "temp_range": (21, 27), "optimal_rain": 600},
        "jute": {"base": 2.5, "max": 4.0, "temp_range": (24, 35), "optimal_rain": 1200},
        
        # Cash Crops
        "sugarcane": {"base": 60.0, "max": 130.0, "temp_range": (26, 32), "optimal_rain": 1200},
        "tobacco": {"base": 1.8, "max": 3.5, "temp_range": (20, 30), "optimal_rain": 500},
        
        # Vegetable Crops
        "tomato": {"base": 18.0, "max": 65.0, "temp_range": (20, 25), "optimal_rain": 600},
        "potato": {"base": 22.0, "max": 52.0, "temp_range": (15, 20), "optimal_rain": 500},
        "onion": {"base": 18.0, "max": 42.0, "temp_range": (13, 24), "optimal_rain": 400},
        "cabbage": {"base": 28.0, "max": 58.0, "temp_range": (15, 20), "optimal_rain": 500},
        "carrot": {"base": 22.0, "max": 48.0, "temp_range": (16, 18), "optimal_rain": 400},
        "cauliflower": {"base": 20.0, "max": 45.0, "temp_range": (15, 20), "optimal_rain": 450},
        "brinjal": {"base": 15.0, "max": 35.0, "temp_range": (22, 32), "optimal_rain": 500},
        "okra": {"base": 8.0, "max": 18.0, "temp_range": (24, 35), "optimal_rain": 400},
        "cucumber": {"base": 12.0, "max": 25.0, "temp_range": (18, 24), "optimal_rain": 450},
        "pumpkin": {"base": 15.0, "max": 30.0, "temp_range": (18, 27), "optimal_rain": 500},
        
        # Legume Crops
        "beans": {"base": 1.5, "max": 3.8, "temp_range": (18, 24), "optimal_rain": 400},
        "peas": {"base": 1.2, "max": 3.0, "temp_range": (10, 18), "optimal_rain": 300},
        "chickpea": {"base": 1.0, "max": 2.5, "temp_range": (20, 30), "optimal_rain": 300},
        "lentil": {"base": 0.8, "max": 2.0, "temp_range": (18, 30), "optimal_rain": 250},
        "blackgram": {"base": 0.6, "max": 1.5, "temp_range": (25, 35), "optimal_rain": 400},
        "greengram": {"base": 0.8, "max": 1.8, "temp_range": (25, 35), "optimal_rain": 350},
        
        # Spice Crops
        "chilli": {"base": 2.5, "max": 6.0, "temp_range": (20, 30), "optimal_rain": 600},
        "turmeric": {"base": 3.0, "max": 8.0, "temp_range": (20, 30), "optimal_rain": 1000},
        "coriander": {"base": 1.0, "max": 2.2, "temp_range": (20, 30), "optimal_rain": 400},
        "cumin": {"base": 0.8, "max": 1.8, "temp_range": (25, 30), "optimal_rain": 300},
        "fenugreek": {"base": 1.2, "max": 2.5, "temp_range": (20, 30), "optimal_rain": 350},
        
        # Fruit Crops (Annual yield)
        "watermelon": {"base": 20.0, "max": 45.0, "temp_range": (24, 35), "optimal_rain": 400},
        "muskmelon": {"base": 15.0, "max": 35.0, "temp_range": (24, 35), "optimal_rain": 350},
        "papaya": {"base": 40.0, "max": 80.0, "temp_range": (22, 32), "optimal_rain": 1200},
        
        # Other Important Crops
        "coconut": {"base": 8.0, "max": 15.0, "temp_range": (27, 32), "optimal_rain": 1200},
        "arecanut": {"base": 1.0, "max": 2.5, "temp_range": (20, 32), "optimal_rain": 1300},
        "ginger": {"base": 8.0, "max": 18.0, "temp_range": (19, 30), "optimal_rain": 1500},
        "garlic": {"base": 6.0, "max": 15.0, "temp_range": (15, 25), "optimal_rain": 300}
    }

def calculate_yield_prediction(soil_temp, ph, rainfall, selected_crop):
    """Advanced yield prediction algorithm considering multiple environmental factors"""
    crop_database = get_yield_prediction_data()
    crop_key = normalize(selected_crop)
    
    # Find matching crop (flexible matching)
    crop_data = None
    for key, data in crop_database.items():
        if crop_key == key or crop_key in key or key in crop_key:
            crop_data = data
            break
    
    # Use default values if crop not found in database
    if not crop_data:
        crop_data = {"base": 2.0, "max": 5.0, "temp_range": (20, 25), "optimal_rain": 500}
    
    # Extract optimal conditions
    optimal_temp = crop_data["temp_range"]
    optimal_rain = crop_data["optimal_rain"]
    temp_mid = (optimal_temp[0] + optimal_temp[1]) / 2
    temp_range = optimal_temp[1] - optimal_temp[0]
    
    # Calculate temperature factor (bell curve)
    temp_factor = max(0.1, min(1.0, 1 - abs(soil_temp - temp_mid) / (temp_range + 5)))
    
    # pH factor (most crops prefer 6.0-7.5)
    optimal_ph = 6.5
    ph_factor = max(0.1, min(1.0, 1 - abs(ph - optimal_ph) / 2.5))
    
    # Rainfall factor
    rain_factor = max(0.1, min(1.0, min(rainfall / optimal_rain, 1.8 - rainfall / (optimal_rain * 1.5))))
    
    # Weighted average of factors with some randomness for realism
    base_score = (temp_factor * 0.35 + ph_factor * 0.25 + rain_factor * 0.4)
    
    # Add slight variation to make predictions more realistic
    import random
    variation = random.uniform(0.95, 1.05)
    overall_score = min(1.0, base_score * variation)
    
    return overall_score, {
        'temp_factor': temp_factor,
        'ph_factor': ph_factor,
        'rain_factor': rain_factor,
        'optimal_temp': optimal_temp,
        'optimal_rain': optimal_rain,
        'crop_data': crop_data
    }

def get_yield_crops():
    """Return list of crops available for yield prediction"""
    crop_database = get_yield_prediction_data()
    return sorted(crop_database.keys())
