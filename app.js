// Main Application Logic and Initialization
// Global variables
const API = "http://127.0.0.1:5000";
let currentLang = "en";
let serverStatus = false;
let currentTab = "recommendation";
let translatedTexts = {};
let isTranslating = false;
let selectedRating = 0;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  initializeApp();
  setupEventListeners();
});

async function initializeApp() {
  await checkServerStatus();
  
  // Check if user is already logged in
  const loggedIn = sessionStorage.getItem("loggedIn");
  if (loggedIn === "true") {
    const storedLang = sessionStorage.getItem("lang") || "en";
    currentLang = storedLang;
    document.getElementById("lang-switch").value = currentLang;
    showCrop();
    await applyTranslations(currentLang);
    await loadOptions();
  }
}

function setupEventListeners() {
  // Star rating functionality
  const stars = document.querySelectorAll('.star');
  const ratingDisplay = document.getElementById('rating-display');
  
  stars.forEach(star => {
    star.addEventListener('click', function() {
      selectedRating = parseInt(this.dataset.rating);
      updateStarRating(selectedRating);
    });
    
    star.addEventListener('mouseover', function() {
      const rating = parseInt(this.dataset.rating);
      updateStarRating(rating, true);
    });
  });
  
  document.querySelector('.star-rating').addEventListener('mouseleave', function() {
    updateStarRating(selectedRating);
  });

  // Seed change listener for related options
  const seedSelect = document.getElementById("seed");
  if (seedSelect) {
    seedSelect.addEventListener("change", async () => {
      const seed = seedSelect.value;
      if (!seed) return;
      
      try {
        const username = sessionStorage.getItem("username");
        const res = await safeFetch(API + "/get_related_options", {
          method: "POST",
          body: JSON.stringify({seed, lang: currentLang, username})
        });
        const data = await res.json();
        if (data.error) { 
          console.error(data.error); 
          return; 
        }
        await populateTranslated("soil", data.soil || []);
        await populateTranslated("season", data.season || []);
        await populateTranslated("location", data.states || []);
      } catch (err) { 
        console.error("related options error", err); 
      }
    });
  }

  // Enter key listeners for login/register forms
  document.getElementById('login-password').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      login();
    }
  });

  document.getElementById('reg-password').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      register();
    }
  });
}

// Tab functionality
function switchTab(tabName) {
  document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
  
  document.getElementById(tabName + '-tab').classList.add('active');
  document.getElementById(tabName + '-content').classList.add('active');
  
  currentTab = tabName;
  
  // Clear previous results when switching tabs
  if (tabName === 'recommendation') {
    document.getElementById("yield-result").innerHTML = "";
  } else if (tabName === 'yield') {
    document.getElementById("recommendation-result").innerHTML = "";
  }
  
  // Load appropriate data based on tab
  if (tabName === 'userinfo') {
    loadUserProfile();
  } else {
    loadOptions();
  }
}

// Check server status
async function checkServerStatus() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    
    const response = await fetch(API + "/health", {
      method: "GET",
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok) {
      const data = await response.json();
      if (data.status === "OK") {
        serverStatus = true;
        document.getElementById("status-indicator").className = "status-indicator status-online";
        document.getElementById("status-indicator").textContent = "Connected";
        return true;
      }
    }
    throw new Error("Server not responding properly");
  } catch (error) {
    serverStatus = false;
    document.getElementById("status-indicator").className = "status-indicator status-offline";
    document.getElementById("status-indicator").textContent = "Server Error";
    console.error("Server status check failed:", error);
    return false;
  }
}

// Enhanced fetch with error handling and retries
async function safeFetch(url, options = {}, retries = 2) {
  for (let i = 0; i <= retries; i++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000);
      
      const response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options.headers
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      console.error(`Attempt ${i + 1} failed for ${url}:`, error);
      
      if (i === retries) {
        if (error.name === 'AbortError') {
          throw new Error("Request timeout - server may be busy");
        }
        throw error;
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}

function clearMessages() {
  document.getElementById("login-error").innerText = "";
  document.getElementById("reg-error").innerText = "";
}

function setButtonLoading(buttonId, isLoading, originalText = "") {
  const button = document.getElementById(buttonId);
  if (isLoading) {
    button.disabled = true;
    button.innerHTML = `<span class="loading"></span>Loading...`;
  } else {
    button.disabled = false;
    button.innerHTML = originalText || button.textContent;
  }
}

// Utility functions
function getLanguageName(langCode) {
  const languages = {
    'en': 'English',
    'hi': 'हिन्दी',
    'ta': 'தமிழ்',
    'te': 'తెలుగు',
    'kn': 'ಕನ್ನಡ',
    'ml': 'മലയാളം',
    'bn': 'বাংলা',
    'gu': 'ગુજરાતી',
    'mr': 'मराठी',
    'pa': 'ਪੰਜਾਬੀ',
    'ur': 'اردو'
  };
  return languages[langCode] || langCode;
}

// Load options based on current tab
async function loadOptions() {
  try {
    const res = await safeFetch(API + "/get_options?lang=" + encodeURIComponent(currentLang) + "&tab=" + encodeURIComponent(currentTab));
    const data = await res.json();
    
    if (data.error) { 
      console.error("get_options error:", data.error); 
      return; 
    }
    
    if (currentTab === 'recommendation') {
      await populateTranslated("seed", data.seed || []);
      await populateTranslated("soil", data.soil || []);
      await populateTranslated("season", data.season || []);
      await populateTranslated("location", data.states || []);
    } else if (currentTab === 'yield') {
      await populateTranslated("yield-seed", data.seed || []);
    }
  } catch (err) { 
    console.error("loadOptions error", err);
    alert("Failed to load options. Please refresh the page.");
  }
}

// Populate select elements with translated options
async function populateTranslated(id, values) {
  const select = document.getElementById(id);
  if (!select) return;
  
  const selectText = getTranslatedText("-- Select --") || "-- Select --";
  select.innerHTML = `<option value="">${selectText}</option>`;
  
  values.forEach(v => {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = v;
    select.appendChild(opt);
  });
}

// Get translated text helper
function getTranslatedText(englishText, key = null) {
  if (currentLang === "en") return englishText;
  
  if (key && translatedTexts[key]) return translatedTexts[key];
  
  return englishText;
}
