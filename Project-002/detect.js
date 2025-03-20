document.addEventListener("DOMContentLoaded", () => {
    const analyzeBtn = document.getElementById("analyzeBtn");
    const resultContainer = document.getElementById("result-container");

    analyzeBtn.addEventListener("click", () => {
        const videoInput = document.getElementById("videoUpload").files[0];

        if (!videoInput) {
            resultContainer.innerHTML = "<p style='color: red;'>❌ Please upload a video first.</p>";
            return;
        }

        // Simulate analysis (Placeholder - Backend Needed)
        resultContainer.innerHTML = "<p>🔍 Analyzing... Please wait.</p>";
        setTimeout(() => {
            resultContainer.innerHTML = "<p style='color: green;'>✅ Analysis Complete! (Backend Integration Needed)</p>";
        }, 3000);
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const logoutBtn = document.getElementById("logoutBtn");

    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            console.log("Logging out...");

            // Clear login status
            localStorage.removeItem("isLoggedIn");
            localStorage.removeItem("redirectAfterLogin");

            // Redirect to index.html
            window.location.href = "index.html";
        });
    }
});
