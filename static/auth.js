// Import the shared Firebase auth instance from the config module
import { auth } from "/static/firebase-config.js";
// Import the individual Firebase auth functions needed by this page
import {
  signInWithEmailAndPassword,      // Signs an existing user in with email and password
  createUserWithEmailAndPassword,  // Registers a new user with email and password
  GoogleAuthProvider,              // Represents the Google OAuth identity provider
  signInWithPopup,                 // Opens a browser popup for OAuth sign-in flows
  onAuthStateChanged               // Subscribes to auth state change events
} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";

// Cache the error element so every handler can reuse it without re-querying the DOM
const errorDiv = document.getElementById("auth-error");

// Displays a Firebase error message inside the error div
function showError(msg) {
  errorDiv.textContent = msg;       // Set the error text content
  errorDiv.style.display = "block"; // Reveal the hidden element so the user can see it
}

// Redirect if already logged in
onAuthStateChanged(auth, (user) => {
  // If a session already exists, skip the login page and go straight home
  if (user) window.location.href = "/";
});

// Wire up the Log In button to sign in with email and password
document.getElementById("login-btn").addEventListener("click", async () => {
  const email = document.getElementById("email").value;        // Read the email input value
  const password = document.getElementById("password").value;  // Read the password input value
  try {
    await signInWithEmailAndPassword(auth, email, password); // Ask Firebase to authenticate
    window.location.href = "/";                              // Redirect home on success
  } catch (e) {
    showError(e.message); // Show the Firebase error message to the user
  }
});

// Wire up the Create Account button to register a new user with email and password
document.getElementById("signup-btn").addEventListener("click", async () => {
  const email = document.getElementById("email").value;        // Read the email input value
  const password = document.getElementById("password").value;  // Read the password input value
  try {
    await createUserWithEmailAndPassword(auth, email, password); // Ask Firebase to create account
    window.location.href = "/";                                  // Redirect home on success
  } catch (e) {
    showError(e.message); // Show the Firebase error message to the user
  }
});

// Wire up the Sign in with Google button for OAuth sign-in via popup
document.getElementById("google-btn").addEventListener("click", async () => {
  const provider = new GoogleAuthProvider(); // Create a Google OAuth provider instance
  try {
    await signInWithPopup(auth, provider); // Open the Google sign-in popup
    window.location.href = "/";            // Redirect home on success
  } catch (e) {
    showError(e.message); // Show the Firebase error message to the user
  }
});
