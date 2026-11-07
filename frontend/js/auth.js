/**
 * CYBERAI Authentication Script
 * Handles registration and login interactions with real-time validation.
 */

document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");

  // ===============================
  // Login Form Submission
  // ===============================
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const submitBtn = loginForm.querySelector("button[type='submit']");
      const usernameInput = document.getElementById("login-username");
      const passwordInput = document.getElementById("login-password");
      const errorBanner = document.getElementById("auth-error-banner");

      const username = usernameInput.value.trim();
      const password = passwordInput.value;

      if (!username || !password) {
        showError(errorBanner, "Foydalanuvchi nomi va parolni kiriting.");
        return;
      }

      setLoading(submitBtn, true, "Kirilmoqda...");

      try {
        const response = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok && data.access_token) {
          localStorage.setItem("cyberai_token", data.access_token);
          localStorage.setItem("cyberai_user", JSON.stringify(data.user));
          showToast("Muvaffaqiyatli tizimga kirildi!", "success");
          setTimeout(() => {
            window.location.href = "/";
          }, 400);
        } else {
          const detail = data.detail || "Kirishda xatolik yuz berdi.";
          showError(errorBanner, detail);
          setLoading(submitBtn, false, "Tizimga Kirish");
        }
      } catch (err) {
        showError(errorBanner, "Server bilan bog'lanishda xatolik yuz berdi.");
        setLoading(submitBtn, false, "Tizimga Kirish");
      }
    });
  }

  // ===============================
  // Registration Form Submission
  // ===============================
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const submitBtn = registerForm.querySelector("button[type='submit']");
      const usernameInput = document.getElementById("reg-username");
      const emailInput = document.getElementById("reg-email");
      const passwordInput = document.getElementById("reg-password");
      const confirmInput = document.getElementById("reg-confirm-password");
      const errorBanner = document.getElementById("auth-error-banner");

      const username = usernameInput.value.trim();
      const email = emailInput.value.trim();
      const password = passwordInput.value;
      const confirmPass = confirmInput.value;

      // Validation
      if (username.length < 3) {
        showError(errorBanner, "Foydalanuvchi nomi kamida 3 belgidan iborat bo'lishi kerak.");
        return;
      }

      if (!email.includes("@") || !email.includes(".")) {
        showError(errorBanner, "To'g'ri elektron pochta manzilini kiriting.");
        return;
      }

      if (password.length < 8) {
        showError(errorBanner, "Parol kamida 8 belgidan iborat bo'lishi kerak.");
        return;
      }

      const hasLetter = /[a-zA-Z]/.test(password);
      const hasNumber = /[0-9]/.test(password);
      if (!hasLetter || !hasNumber) {
        showError(errorBanner, "Parol kamida bitta harf va bitta raqamdan iborat bo'lishi kerak.");
        return;
      }

      if (password !== confirmPass) {
        showError(errorBanner, "Kiritilgan parollar bir-biriga mos kelmadi.");
        return;
      }

      setLoading(submitBtn, true, "Ro'yxatdan o'tilmoqda...");

      try {
        const response = await fetch("/api/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (response.ok && data.access_token) {
          localStorage.setItem("cyberai_token", data.access_token);
          localStorage.setItem("cyberai_user", JSON.stringify(data.user));
          showToast("Akkaunt muvaffaqiyatli yaratildi!", "success");
          setTimeout(() => {
            window.location.href = "/";
          }, 400);
        } else {
          const detail = data.detail || "Ro'yxatdan o'tishda xatolik yuz berdi.";
          showError(errorBanner, detail);
          setLoading(submitBtn, false, "Ro'yxatdan O'tish");
        }
      } catch (err) {
        showError(errorBanner, "Server bilan bog'lanishda xatolik yuz berdi.");
        setLoading(submitBtn, false, "Ro'yxatdan O'tish");
      }
    });
  }

  function showError(element, msg) {
    if (element) {
      element.textContent = msg;
      element.style.display = "block";
    } else {
      showToast(msg, "error");
    }
  }

  function setLoading(btn, isLoading, text) {
    if (!btn) return;
    btn.disabled = isLoading;
    btn.textContent = text;
    btn.style.opacity = isLoading ? "0.7" : "1";
  }
});
