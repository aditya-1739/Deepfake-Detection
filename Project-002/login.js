document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const signupForm = document.getElementById("signupForm");

    const showSignup = document.getElementById("show-signup");
    const showLogin = document.getElementById("show-login");

    const loginContainer = document.getElementById("login-form");
    const signupContainer = document.getElementById("signup-form");

    const loginError = document.getElementById("login-error");
    const signupError = document.getElementById("signup-error");
    const signupSuccess = document.getElementById("signup-success");

    // Switch between login and signup forms
    function switchForm(hide, show) {
        hide.style.display = "none";
        show.style.display = "block";
    }

    showSignup.addEventListener("click", () => switchForm(loginContainer, signupContainer));
    showLogin.addEventListener("click", () => switchForm(signupContainer, loginContainer));

    // ✅ REGISTER USER
    signupForm.addEventListener("submit", (e) => {
        e.preventDefault(); // Prevent form from reloading the page

        const signupEmail = document.getElementById("signup-email").value.trim().toLowerCase();
        const signupPassword = document.getElementById("signup-password").value.trim();

        if (signupEmail === "" || signupPassword === "") {
            signupError.textContent = "⚠️ Please fill in all fields.";
            signupError.style.display = "block";
            return;
        }

        // Store credentials in localStorage
        localStorage.setItem("userEmail", signupEmail);
        localStorage.setItem("userPassword", signupPassword);

        console.log("✅ Registered User:", signupEmail, signupPassword); // Debugging Log

        signupError.style.display = "none";
        signupSuccess.textContent = "✅ Registration successful! You can now log in.";
        signupSuccess.style.display = "block";

        // Clear the input fields
        document.getElementById("signup-email").value = "";
        document.getElementById("signup-password").value = "";

        // After 2 seconds, switch to login form
        setTimeout(() => {
            switchForm(signupContainer, loginContainer);
            signupSuccess.style.display = "none";
        }, 2000);
    });

    // ✅ LOGIN USER
    loginForm.addEventListener("submit", (e) => {
        e.preventDefault(); // Prevent form reload

        const email = document.getElementById("login-email").value.trim().toLowerCase();
        const password = document.getElementById("login-password").value.trim();

        const storedEmail = localStorage.getItem("userEmail");
        const storedPassword = localStorage.getItem("userPassword");

        console.log("🔎 Stored User:", storedEmail, storedPassword); // Debugging Log
        console.log("🔎 Entered User:", email, password); // Debugging Log

        if (email === storedEmail && password === storedPassword) {
            loginError.style.display = "none";
            window.location.href = "detect.html"; // Redirect to homepage after login
        } else {
            loginError.textContent = "❌ Invalid email or password! Please try again.";
            loginError.style.display = "block";
        }
    });
});






document.addEventListener("DOMContentLoaded", () => {
    const signupContainer = document.getElementById("signup-form");
    const loginContainer = document.getElementById("login-form");
    
    const showSignup = document.getElementById("show-signup");
    const showLogin = document.getElementById("show-login");

    showSignup.addEventListener("click", () => {
        loginContainer.style.display = "none";
        signupContainer.style.display = "block";
    });

    showLogin.addEventListener("click", () => {
        signupContainer.style.display = "none";
        loginContainer.style.display = "block";
    });
});
