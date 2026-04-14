import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyB2PHHd0ZK5R_OIQTavEpV130PKgsMnipo",
  authDomain: "chefgpt-users.firebaseapp.com",
  projectId: "chefgpt-users",
  storageBucket: "chefgpt-users.firebasestorage.app",
  messagingSenderId: "579326410935",
  appId: "1:579326410935:web:173b12498ea10519954d32",
  measurementId: "G-2KPS1GC009"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);