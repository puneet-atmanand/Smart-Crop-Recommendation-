// Crop Recommendation Tab
// Functions for getting crop recommendations

// Get crop recommendation
async function getInfo() {
    const seed = document.getElementById("seed").value;
    const soil = document.getElementById("soil").value;
    const season = document.getElementById("season").value;
    const location = document.getElementById("location").value;
    const resultDiv = document.getElementById("recommendation-result");
    const username = sessionStorage.getItem("username");

    if (!seed || !soil || !season || !location) {
        resultDiv.innerHTML = `<p class="error">Please fill in all fields</p>`;
        return;
    }

    setButtonLoading("recommend-btn", true);
    resultDiv.innerHTML = `<p>Fetching recommendation...</p>`;

    try {
        const response = await safeFetch(API + "/get_crop_info", {
            method: "POST",
            body: JSON.stringify({ seed, soil, season, location, lang: currentLang, username })
        });

        const data = await response.json();

        if (!response.ok) {
            resultDiv.innerHTML = `<p class="error">${data.error || "No match found"}</p>`;
            return;
        }

        resultDiv.innerHTML = `
      <img src="https://source.unsplash.com/400x300/?${encodeURIComponent(data.seed)}" 
           alt="${data.seed}" 
           onerror="this.src='https://via.placeholder.com/400x300/4caf50/white?text=${encodeURIComponent(data.seed)}'">
      <h2>${data.seed}</h2>
      <div style="text-align: left; max-width: 600px; margin: 0 auto;">
        <p><strong>Information:</strong> ${data.info}</p>
        <p><strong>Growth Days:</strong> ${data.growth_days}</p>
        <p><strong>Fertilizers:</strong> ${data.fertilizers}</p>
        <p><strong>Irrigation:</strong> ${data.irrigation}</p>
      </div>`;
    } catch (err) {
        console.error("getInfo error:", err);
        resultDiv.innerHTML = `<p class="error">Error connecting to backend. Please check server status.</p>`;
    } finally {
        setButtonLoading("recommend-btn", false, "Get Recommendation");
    }
}
