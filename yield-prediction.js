// Yield Prediction Tab
// Functions for predicting crop yield

// Predict yield
async function predictYield() {
    const soil_temp = parseFloat(document.getElementById("soil_temp").value || 0);
    const ph = parseFloat(document.getElementById("ph").value || 0);
    const rainfall = parseFloat(document.getElementById("rainfall").value || 0);
    const selected_crop = document.getElementById("yield-seed").value;
    const div = document.getElementById("yield-result");
    const username = sessionStorage.getItem("username");

    // Input validation
    if (soil_temp <= 0 || soil_temp > 50) {
        div.innerHTML = `<p class="error">Please provide a valid soil temperature between 1-50°C</p>`;
        return;
    }

    if (ph <= 0 || ph > 14) {
        div.innerHTML = `<p class="error">Please provide a valid pH value between 1-14</p>`;
        return;
    }

    if (rainfall < 0 || rainfall > 5000) {
        div.innerHTML = `<p class="error">Please provide a valid rainfall amount (0-5000mm)</p>`;
        return;
    }

    if (!selected_crop) {
        div.innerHTML = `<p class="error">Please select a crop first to predict yield</p>`;
        return;
    }

    setButtonLoading("yield-btn", true);
    div.innerHTML = `<p>Analyzing environmental conditions and predicting yield...</p>`;

    try {
        const res = await safeFetch(API + "/predict_yield", {
            method: "POST",
            body: JSON.stringify({
                soil_temp,
                ph,
                rainfall,
                selected_crop: selected_crop,
                lang: currentLang,
                username
            })
        });

        const data = await res.json();

        if (!res.ok) {
            div.innerHTML = `<p class="error">${data.error || "Prediction failed"}</p>`;
            return;
        }

        // Enhanced yield result display
        div.innerHTML = `
      <div class="yield-display">
        <h3>Predicted Yield for ${data.crop}</h3>
        <div class="yield-value">${data.predicted_yield} ${data.units}</div>
        <div class="quality-badge" style="background-color: ${data.quality_color};">
          Quality: ${data.quality}
        </div>
        <div style="margin: 15px 0; font-size: 16px;">
          <strong>Confidence Score: ${data.confidence_score}%</strong>
        </div>
      </div>
      
      <div class="factors-grid">
        <div class="factor-card">
          <div class="factor-score">${data.factors.temp_score}%</div>
          <div>Temperature Score</div>
          <div style="font-size: 12px; opacity: 0.7;">Input: ${data.factors.soil_temperature}°C</div>
        </div>
        <div class="factor-card">
          <div class="factor-score">${data.factors.ph_score}%</div>
          <div>pH Score</div>
          <div style="font-size: 12px; opacity: 0.7;">Input: ${data.factors.ph_level}</div>
        </div>
        <div class="factor-card">
          <div class="factor-score">${data.factors.rain_score}%</div>
          <div>Rainfall Score</div>
          <div style="font-size: 12px; opacity: 0.7;">Input: ${data.factors.rainfall}mm</div>
        </div>
      </div>
      
      ${data.optimal_conditions ? `
      <div class="optimal-conditions">
        <h4>Optimal Conditions for ${data.crop}</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
          <div><strong>Temperature:</strong> ${data.optimal_conditions.temperature_range}</div>
          <div><strong>pH Level:</strong> ${data.optimal_conditions.ph_range}</div>
          <div><strong>Rainfall:</strong> ${data.optimal_conditions.optimal_rainfall}</div>
        </div>
      </div>
      ` : ''}
      
      ${data.yield_range ? `
      <div style="background: rgba(255,255,255,0.08); padding: 20px; border-radius: 12px; margin: 20px 0;">
        <h4>Yield Range Analysis</h4>
        <div style="display: flex; justify-content: space-around; text-align: center; flex-wrap: wrap;">
          <div style="margin: 10px;">
            <div style="font-size: 18px; font-weight: bold; color: #ff5722;">
              ${data.yield_range.minimum} t/ha
            </div>
            <div>Minimum Expected</div>
          </div>
          <div style="margin: 10px;">
            <div style="font-size: 18px; font-weight: bold; color: #4caf50;">
              ${data.predicted_yield} t/ha
            </div>
            <div>Your Prediction</div>
          </div>
          <div style="margin: 10px;">
            <div style="font-size: 18px; font-weight: bold; color: #2196f3;">
              ${data.yield_range.maximum} t/ha
            </div>
            <div>Maximum Possible</div>
          </div>
        </div>
      </div>
      ` : ''}
      
      ${data.recommendations && data.recommendations.length > 0 ? `
      <div class="recommendations-box">
        <h4>Agricultural Recommendations</h4>
        ${data.recommendations.map(rec => `<div class="rec-item">• ${rec}</div>`).join('')}
      </div>
      ` : ''}
      
      <div style="background: rgba(76,175,80,0.1); padding: 15px; border-radius: 10px; margin-top: 20px; text-align: center; font-size: 13px; opacity: 0.8;">
        <strong>Algorithm:</strong> Advanced multi-factor prediction considering temperature optimization, pH balance, rainfall adequacy, and crop-specific characteristics from a comprehensive agricultural database.
      </div>
    `;

        console.log("Yield prediction successful:", data);
    } catch (err) {
        console.error("predictYield error:", err);
        div.innerHTML = `<p class="error">Error connecting to backend. Please check server status.</p>`;
    } finally {
        setButtonLoading("yield-btn", false, "Predict Yield");
    }
}
