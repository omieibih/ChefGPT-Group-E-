// Import the Firebase app initializer — must be called before using any Firebase service
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
// Import the Firebase Authentication service factory
import { getAuth } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";
// Import the Firestore (NoSQL database) service factory
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js";

// Firebase project configuration — values come from the Firebase Console
const firebaseConfig = {
  // Firebase Web API key belongs here (client-side key, not the Admin SDK private key).
  apiKey: "AIzaSyB2PHHd0ZK5R_OIQTavEpV130PKgsMnipo",
  authDomain: "chefgpt-users.firebaseapp.com",        // Domain used for OAuth redirects
  projectId: "chefgpt-users",                          // Identifies the Firestore database project
  storageBucket: "chefgpt-users.firebasestorage.app",  // Cloud Storage bucket (not used here)
  messagingSenderId: "579326410935",                   // Sender ID required by Firebase Messaging
  appId: "1:579326410935:web:173b12498ea10519954d32",  // Unique ID for this web app registration
  measurementId: "G-2KPS1GC009"                        // Google Analytics measurement ID
};

// Bootstrap the Firebase SDK with the config above — all services share this single app instance
const app = initializeApp(firebaseConfig);
// Export the Auth instance so sign-in pages can import and use it directly
export const auth = getAuth(app);
// Export the Firestore instance so data pages can read and write user documents
export const db = getFirestore(app);
