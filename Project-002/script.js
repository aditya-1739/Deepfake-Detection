document.addEventListener("DOMContentLoaded", () => {
    const sections = document.querySelectorAll(".scroll-reveal");

    const revealOnScroll = () => {
        sections.forEach(section => {
            const sectionTop = section.getBoundingClientRect().top;
            if (sectionTop < window.innerHeight - 50) {
                section.style.opacity = "1";
                section.style.transform = "translateY(0)";
            }
        });
    };

    window.addEventListener("scroll", revealOnScroll);
    revealOnScroll(); // Trigger on page load
});

document.addEventListener("DOMContentLoaded", function () {
    const deepfakeLink = document.querySelector("a[href='detect.html']"); // Detect button link
    const loginStatus = localStorage.getItem("isLoggedIn"); // Check login status

    if (deepfakeLink) {
        deepfakeLink.addEventListener("click", function (event) {
            if (loginStatus !== "true") {
                event.preventDefault();
                console.log("Redirecting to login page, storing redirectAfterLogin...");
                localStorage.setItem("redirectAfterLogin", "detect.html"); // Store where to go after login
                console.log("Stored redirectAfterLogin:", localStorage.getItem("redirectAfterLogin"));
                window.location.href = "login.html";
            }
        });
    }
});


if (window.location.pathname.includes("login.html")) {
    document.addEventListener("submit", function (event) {
        if (event.target.id === "loginForm") {
            event.preventDefault();

            const email = document.getElementById("login-email").value.trim();
            const password = document.getElementById("login-password").value.trim();
            const storedEmail = localStorage.getItem("userEmail");
            const storedPassword = localStorage.getItem("userPassword");

            console.log("Login Attempt: ", email, password);
            console.log("Stored Credentials: ", storedEmail, storedPassword);
            console.log("Redirect After Login:", localStorage.getItem("redirectAfterLogin"));

            if (email === storedEmail && password === storedPassword) {
                localStorage.setItem("isLoggedIn", "true");

                const redirectPage = localStorage.getItem("redirectAfterLogin");

                if (redirectPage) {
                    console.log("✅ Redirecting to:", redirectPage);
                    localStorage.removeItem("redirectAfterLogin");
                    window.location.href = redirectPage;
                } else {
                    console.log("⚠️ No stored redirect found, going to detect.html");
                    window.location.href = "detect.html"; // Default redirect
                }
            } else {
                console.log("❌ Invalid login attempt");
                document.getElementById("login-error").textContent = "❌ Invalid email or password!";
                document.getElementById("login-error").style.display = "block";
            }
        }
    });
}
