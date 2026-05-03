import { auth } from "/static/firebase-config.js";
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  GoogleAuthProvider,
  signInWithPopup,
  onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";

const errorDiv = document.getElementById("auth-error");

function showError(msg) {
  errorDiv.textContent = msg;
  errorDiv.style.display = "block";
}

// Redirect if already logged in
onAuthStateChanged(auth, (user) => {
  if (user) window.location.href = "/";
});

document.getElementById("login-btn").addEventListener("click", async () => {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  try {
    await signInWithEmailAndPassword(auth, email, password);
    window.location.href = "/";
  } catch (e) {
    showError(e.message);
  }
});

document.getElementById("signup-btn").addEventListener("click", async () => {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  try {
    await createUserWithEmailAndPassword(auth, email, password);
    window.location.href = "/";
  } catch (e) {
    showError(e.message);
  }
});

document.getElementById("google-btn").addEventListener("click", async () => {
  const provider = new GoogleAuthProvider();
  try {
    await signInWithPopup(auth, provider);
    window.location.href = "/";
  } catch (e) {
    showError(e.message);
  }
});