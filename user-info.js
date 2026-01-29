// User Info Tab
// Functions for user profile, feedback, and star rating

function updateStarRating(rating, isHover = false) {
    const stars = document.querySelectorAll('.star');
    const ratingDisplay = document.getElementById('rating-display');

    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });

    if (!isHover) {
        if (rating > 0) {
            ratingDisplay.textContent = `${rating}/5 stars selected`;
        } else {
            ratingDisplay.textContent = "No rating selected";
        }
    }
}

// Load user profile
async function loadUserProfile() {
    const username = sessionStorage.getItem("username");
    if (!username) return;

    try {
        const res = await safeFetch(API + "/get_user_profile", {
            method: "POST",
            body: JSON.stringify({ username })
        });

        const data = await res.json();

        if (!res.ok) {
            document.getElementById("profile-content").innerHTML = `<p class="error">Error: ${data.error}</p>`;
            return;
        }

        document.getElementById("profile-content").innerHTML = `
      <div class="profile-item">
        <span><strong>Username:</strong></span>
        <span>${data.username}</span>
      </div>
      <div class="profile-item">
        <span><strong>Preferred Language:</strong></span>
        <span>${getLanguageName(data.language)}</span>
      </div>
      <div class="profile-item">
        <span><strong>Member Since:</strong></span>
        <span>${data.created_at || 'Unknown'}</span>
      </div>
      <div class="profile-item">
        <span><strong>Last Login:</strong></span>
        <span>${data.last_login || 'Never'}</span>
      </div>
    `;
    } catch (error) {
        console.error("Load profile error:", error);
        document.getElementById("profile-content").innerHTML = `<p class="error">Failed to load profile information</p>`;
    }
}

// Submit feedback
async function submitFeedback() {
    const username = sessionStorage.getItem("username");
    const feedbackText = document.getElementById("feedback-text").value.trim();
    const resultDiv = document.getElementById("feedback-result");

    if (!username) {
        resultDiv.innerHTML = '<p class="error">Please login to submit feedback</p>';
        return;
    }

    if (selectedRating === 0) {
        resultDiv.innerHTML = '<p class="error">Please select a rating</p>';
        return;
    }

    if (!feedbackText) {
        resultDiv.innerHTML = '<p class="error">Please enter your feedback</p>';
        return;
    }

    if (feedbackText.length > 1000) {
        resultDiv.innerHTML = '<p class="error">Feedback is too long (max 1000 characters)</p>';
        return;
    }

    setButtonLoading("submit-feedback-btn", true);
    resultDiv.innerHTML = "";

    try {
        const res = await safeFetch(API + "/submit_feedback", {
            method: "POST",
            body: JSON.stringify({
                username,
                rating: selectedRating,
                feedback: feedbackText
            })
        });

        const data = await res.json();

        if (!res.ok) {
            resultDiv.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }

        resultDiv.innerHTML = `<p class="success">${data.message}</p>`;

        // Clear form
        document.getElementById("feedback-text").value = "";
        selectedRating = 0;
        updateStarRating(0);

    } catch (error) {
        console.error("Submit feedback error:", error);
        resultDiv.innerHTML = '<p class="error">Failed to submit feedback. Please try again.</p>';
    } finally {
        setButtonLoading("submit-feedback-btn", false, "Submit Feedback");
    }
}
