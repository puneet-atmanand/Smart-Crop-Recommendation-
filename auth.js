// Authentication Functions
// Login, Register, Logout functionality

function showRegister() {
    document.getElementById("login-section").classList.add("hidden");
    document.getElementById("register-section").classList.remove("hidden");
    clearMessages();
}

function showLogin() {
    document.getElementById("register-section").classList.add("hidden");
    document.getElementById("login-section").classList.remove("hidden");
    clearMessages();
}

function showCrop() {
    document.getElementById("login-section").classList.add("hidden");
    document.getElementById("register-section").classList.add("hidden");
    document.getElementById("crop-section").classList.remove("hidden");

    switchTab('recommendation');
    applyTranslations(currentLang);
}

// Login functionality
async function login() {
    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value.trim();
    const errorDiv = document.getElementById("login-error");

    if (!username || !password) {
        errorDiv.innerText = "Please enter both username and password";
        return;
    }

    setButtonLoading("login-btn", true);
    errorDiv.innerText = "";

    try {
        const res = await safeFetch(API + "/login", {
            method: "POST",
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (!res.ok) {
            errorDiv.innerText = data.error || "Login failed";
            return;
        }

        currentLang = data.lang || "en";
        sessionStorage.setItem("username", username);
        sessionStorage.setItem("session_id", data.session_id || "");
        sessionStorage.setItem("lang", currentLang);
        sessionStorage.setItem("loggedIn", "true");

        document.getElementById("lang-switch").value = currentLang;
        showCrop();

        await applyTranslations(currentLang);
        await loadOptions();

        console.log(`User ${username} logged in with language: ${currentLang}`);
    } catch (error) {
        console.error("Login error:", error);
        errorDiv.innerText = "Connection error. Please check if server is running.";
    } finally {
        setButtonLoading("login-btn", false, "Login");
    }
}

// Register functionality
async function register() {
    const username = document.getElementById("reg-username").value.trim();
    const password = document.getElementById("reg-password").value.trim();
    const lang = document.getElementById("reg-lang").value;
    const errorDiv = document.getElementById("reg-error");

    if (!username || !password) {
        errorDiv.innerText = "Please enter both username and password";
        return;
    }

    if (username.length < 3) {
        errorDiv.innerText = "Username must be at least 3 characters long";
        return;
    }

    if (password.length < 4) {
        errorDiv.innerText = "Password must be at least 4 characters long";
        return;
    }

    setButtonLoading("register-btn", true);
    errorDiv.innerText = "";

    try {
        const res = await safeFetch(API + "/register", {
            method: "POST",
            body: JSON.stringify({ username, password, lang })
        });

        const data = await res.json();

        if (!res.ok) {
            errorDiv.innerText = data.error || "Registration failed";
            return;
        }

        alert("Registration successful! Please login.");
        currentLang = lang || "en";
        await applyTranslations(currentLang);
        showLogin();

        document.getElementById("login-username").value = username;
    } catch (error) {
        console.error("Register error:", error);
        errorDiv.innerText = "Connection error. Please check if server is running.";
    } finally {
        setButtonLoading("register-btn", false, "Register");
    }
}

// Logout functionality
async function logout() {
    if (!confirm("Are you sure you want to logout?")) {
        return;
    }

    const username = sessionStorage.getItem("username");
    const session_id = sessionStorage.getItem("session_id");

    try {
        await safeFetch(API + "/logout", {
            method: "POST",
            body: JSON.stringify({ username, session_id })
        });
    } catch (error) {
        console.error("Logout error:", error);
    }

    // Clear session data
    sessionStorage.clear();

    // Reset UI
    currentLang = "en";
    translatedTexts = {};
    selectedRating = 0;

    // Show login screen
    document.getElementById("crop-section").classList.add("hidden");
    document.getElementById("login-section").classList.remove("hidden");
    document.getElementById("register-section").classList.add("hidden");

    // Clear forms and results
    document.getElementById("login-username").value = "";
    document.getElementById("login-password").value = "";
    document.getElementById("recommendation-result").innerHTML = "";
    document.getElementById("yield-result").innerHTML = "";
    document.getElementById("feedback-result").innerHTML = "";
    clearMessages();

    // Reset to English
    document.getElementById("lang-switch").value = "en";
    resetToEnglish();
}
