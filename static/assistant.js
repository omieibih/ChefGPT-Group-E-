import { auth } from "/static/firebase-config.js";
import { onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";

// This script powers the floating assistant panel on the page.
// It handles the UI only: opening and closing the panel, rendering chips,
// calling the backend for personalized suggestions, and letting the user add
// ingredients into the form.
// Keeping these concerns in one place makes the behavior easy to demo.
// The page logic is split this way on purpose: the backend decides what data
// to return, and this file decides how to show it to the user.

// Cache the assistant UI elements so the script can update the panel without
// repeatedly querying the DOM.
const bubble = document.getElementById("assistant-toggle");
const card = document.getElementById("assistant-panel");
const text = document.getElementById("assistant-message");
const luckyBtn = document.getElementById("assistant-lucky");
const chips = document.getElementById("assistant-chips");
const input = document.getElementById("ingredients-input") || document.getElementById("ingredients");

// This variable tracks the signed-in Firebase user so the script knows whether
// it can request personalized suggestions from the backend.
let user = null;

// A small pool of starter ingredients used when the user wants a random prompt.
// This is a fallback UI path for when the user wants ideas without using saved
// favorites.
const luckyPool = ["garlic", "onion", "tomato", "rice", "eggs", "chicken", "pasta", "beans", "carrot", "mushroom", "spinach", "potato"];

// Open and close the assistant panel.
// These functions keep the show/hide logic isolated so the event handlers stay
// simple and readable.
function openCard() {
    card.classList.add("open");
    card.setAttribute("aria-hidden", "false");
}

function closeCard() {
    card.classList.remove("open");
    card.setAttribute("aria-hidden", "true");
}

// Update the status line inside the assistant panel.
// The panel uses this message to tell the user what is happening right now.
function setMessage(message) {
    text.textContent = message;
}

// Replace the current chip list with new buttons.
// Each rendered chip becomes a clickable action that inserts an ingredient
// into the input field.
function renderChips(items) {
    chips.innerHTML = "";

    for (const item of items) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "assistant-chip";
        button.textContent = item;
        button.addEventListener("click", () => addItem(item));
        chips.appendChild(button);
    }
}

// Read the ingredient input as a normalized array so we can compare values
// consistently and avoid duplicate entries.
// This is part of the reliability story: the UI should not create duplicates
// just because the user typed a different case or spacing.
// Data complexity stays low here because the function only has to work with a
// flat list of comma-separated ingredients.
function currentList() {
    if (!input) {
        return [];
    }

    return input.value
        .split(",")
        .map((item) => item.trim().toLowerCase())
        .filter(Boolean);
}

// Add a suggested ingredient into the input field if it is not already there.
// The duplicate check keeps the form clean and prevents the same ingredient
// chip from being added twice.
// Decision complexity is intentionally simple: empty input, duplicate input,
// or valid input are the only three outcomes.
function addItem(item) {
    if (!input) {
        return;
    }

    const clean = item.trim();

    if (!clean) {
        return;
    }

    if (currentList().includes(clean.toLowerCase())) {
        return;
    }

    input.value = input.value.trim() === "" ? clean : input.value.trim() + ", " + clean;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    setMessage("Added " + clean + ". Tap another chip or generate recipes.");
}

// Build a small random set of ingredients and render them as clickable chips.
// This gives the assistant a second mode that does not depend on saved favorites.
// It is useful as a demo-friendly fallback and for users who want a quick idea.
function randomIngredients() {
    const picks = [];

    // Keep sampling until we have a short, unique set.
    while (picks.length < 3 && picks.length < luckyPool.length) {
        const item = luckyPool[Math.floor(Math.random() * luckyPool.length)];
        if (!picks.includes(item)) {
            picks.push(item);
        }
    }

    // Update the message before rendering so the user understands why the list
    // changed and where the ideas came from.
    setMessage("I'm feeling lucky, try these random ingredients:");
    renderChips(picks);
}

// Render API results from the backend into the assistant panel.
// The backend returns a plain JSON object, and this function turns that object
// into a user-facing message plus a list of clickable chips.
// Structural complexity is low because this render step only maps data to UI;
// it does not own auth, fetch, or database work.
function render(data) {
    const title = data.recipe_title || "a recipe you liked";
    const items = Array.isArray(data.suggested_ingredients) ? data.suggested_ingredients : [];

    if (data.no_favorites) {
        // If the user has not saved anything yet, the assistant explains that
        // first instead of showing an empty or confusing state.
        setMessage("Save a favorite recipe first, then I can suggest ingredients.");
    } else {
        // When favorites exist, the message connects the suggestions back to
        // the user's own saved recipe so the experience feels personal.
        setMessage("Since you liked " + title + ", try adding these:");
    }
    renderChips(items);
}

// Fetch ingredient suggestions for the signed-in user.
// This function is the bridge between the UI and the authenticated backend.
// Security lives in the token check here because the request must carry the
// current user's Firebase ID token before personalized data is returned.
async function loadData() {
    if (!user) {
        // Security: if we do not have a signed-in user yet, we stop before
        // making a request that would fail or return the wrong data.
        setMessage("Please log in first.");
        chips.innerHTML = "";
        return;
    }

    // Reliability: clear the panel and show a loading message so the user knows
    // the assistant is working instead of leaving stale chips on the screen.
    setMessage("Thinking about your favorites...");
    chips.innerHTML = "";

    // The backend requires a Firebase ID token, so we ask Firebase for the
    // current user's token right before the request.
    const token = await user.getIdToken();

    // Send the token in the Authorization header so the API can verify access
    // and return only the current user's personalized suggestions.
    const response = await fetch("/api/ingredient-suggestions", {
        headers: { Authorization: "Bearer " + token },
    });

    if (!response.ok) {
        // Reliability: if the API fails, we show a safe error message and clear
        // the chip area so the panel does not keep misleading old content.
        // This keeps the failure mode obvious instead of silently showing stale UI.
        setMessage("Could not load suggestions.");
        chips.innerHTML = "";
        return;
    }

    // The response is JSON, so we pass it into the renderer and let the UI
    // convert backend data into buttons and text.
    render(await response.json());
}

// Keep track of the current Firebase auth user so requests can be authorized.
// This callback stays in sync with the login state across the whole page.
onAuthStateChanged(auth, (firebaseUser) => {
    user = firebaseUser;
});

// Toggle the assistant panel and load personalized suggestions when opened.
// The panel loads data only when the user explicitly opens it, which keeps the
// page light and avoids unnecessary requests.
bubble.addEventListener("click", async () => {
    if (card.classList.contains("open")) {
        closeCard();
        return;
    }

    openCard();
    await loadData();
});

// Show the random ingredient prompt and make each suggestion clickable.
// This is the "surprise me" path for a user who wants inspiration without
// waiting for backend data.
luckyBtn.addEventListener("click", () => {
    openCard();
    randomIngredients();
});

// Close the panel when the user clicks outside it.
// This is standard UI cleanup so the assistant does not stay open forever.
document.addEventListener("click", (event) => {
    if (!card.classList.contains("open")) {
        return;
    }

    // Ignore clicks that happen inside the panel itself or on the bubble button.
    if (card.contains(event.target) || bubble.contains(event.target)) {
        return;
    }

    closeCard();
});
