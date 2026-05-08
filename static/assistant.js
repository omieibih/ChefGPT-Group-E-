// Import the shared Firebase auth instance from the config module
import { auth } from "/static/firebase-config.js";
// Import the auth state listener so the assistant knows who is signed in
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
const bubble = document.getElementById("assistant-toggle");    // The floating action button in the corner
const card = document.getElementById("assistant-panel");        // The expandable suggestion panel
const text = document.getElementById("assistant-message");      // The status/message text element inside the panel
const luckyBtn = document.getElementById("assistant-lucky");    // The "I'm Feeling Lucky" button
const chips = document.getElementById("assistant-chips");       // The container that holds ingredient chip buttons
const input = document.getElementById("ingredients-input") || document.getElementById("ingredients"); // The ingredient text input (id differs by page)

// This variable tracks the signed-in Firebase user so the script knows whether
// it can request personalized suggestions from the backend.
let user = null; // Starts as null; updated by the onAuthStateChanged listener below

// A small pool of starter ingredients used when the user wants a random prompt.
// This is a fallback UI path for when the user wants ideas without using saved
// favorites.
const luckyPool = ["garlic", "onion", "tomato", "rice", "eggs", "chicken", "pasta", "beans", "carrot", "mushroom", "spinach", "potato"]; // Hand-picked common pantry ingredients

// Open and close the assistant panel.
// These functions keep the show/hide logic isolated so the event handlers stay
// simple and readable.
function openCard() {
    card.classList.add("open");                // Add the CSS class that sets display:block
    card.setAttribute("aria-hidden", "false"); // Tell screen readers the panel is now visible
}

function closeCard() {
    card.classList.remove("open");            // Remove the CSS class to hide the panel
    card.setAttribute("aria-hidden", "true"); // Tell screen readers the panel is now hidden
}

// Update the status line inside the assistant panel.
// The panel uses this message to tell the user what is happening right now.
function setMessage(message) {
    text.textContent = message; // Replace whatever text was displayed previously
}

// Replace the current chip list with new buttons.
// Each rendered chip becomes a clickable action that inserts an ingredient
// into the input field.
function renderChips(items) {
    chips.innerHTML = ""; // Clear any previously rendered chips before drawing new ones

    for (const item of items) { // Iterate over each suggested ingredient name
        const button = document.createElement("button"); // Create a new button element for this chip
        button.type = "button";                          // Prevent accidental form submission on click
        button.className = "assistant-chip";             // Apply the pill chip visual style
        button.textContent = item;                       // Label the chip with the ingredient name
        button.addEventListener("click", () => addItem(item)); // Clicking the chip adds the ingredient to the input
        chips.appendChild(button); // Insert the finished chip into the chips container
    }
}

// Read the ingredient input as a normalized array so we can compare values
// consistently and avoid duplicate entries.
// This is part of the reliability story: the UI should not create duplicates
// just because the user typed a different case or spacing.
// Data complexity stays low here because the function only has to work with a
// flat list of comma-separated ingredients.
function currentList() {
    if (!input) { // Guard: if the input element is missing on this page, return empty array
        return [];
    }

    return input.value                              // Read the current comma-separated string
        .split(",")                                 // Split into individual tokens on commas
        .map((item) => item.trim().toLowerCase())   // Normalize whitespace and letter case
        .filter(Boolean);                           // Drop empty strings produced by trailing commas
}

// Add a suggested ingredient into the input field if it is not already there.
// The duplicate check keeps the form clean and prevents the same ingredient
// chip from being added twice.
// Decision complexity is intentionally simple: empty input, duplicate input,
// or valid input are the only three outcomes.
function addItem(item) {
    if (!input) { // Guard: if the input element is missing on this page, do nothing
        return;
    }

    const clean = item.trim(); // Remove leading and trailing whitespace from the ingredient name

    if (!clean) { // Ignore blank strings (e.g., the user passed only whitespace)
        return;
    }

    if (currentList().includes(clean.toLowerCase())) { // Skip if the ingredient is already in the list
        return;
    }

    // Append with a comma separator, or just set the value if the input was previously empty
    input.value = input.value.trim() === "" ? clean : input.value.trim() + ", " + clean;
    input.dispatchEvent(new Event("input", { bubbles: true })); // Notify other listeners that the value changed
    setMessage("Added " + clean + ". Tap another chip or generate recipes."); // Confirm the addition to the user
}

// Build a small random set of ingredients and render them as clickable chips.
// This gives the assistant a second mode that does not depend on saved favorites.
// It is useful as a demo-friendly fallback and for users who want a quick idea.
function randomIngredients() {
    const picks = []; // Accumulator for the randomly selected ingredient names

    // Keep sampling until we have a short, unique set.
    while (picks.length < 3 && picks.length < luckyPool.length) { // Pick up to 3 unique items
        const item = luckyPool[Math.floor(Math.random() * luckyPool.length)]; // Pick a random item from the pool
        if (!picks.includes(item)) { // Only add the item if it has not already been picked
            picks.push(item); // Add the new unique ingredient to the picks array
        }
    }

    // Update the message before rendering so the user understands why the list
    // changed and where the ideas came from.
    setMessage("I'm feeling lucky, try these random ingredients:"); // Show the lucky-mode prompt
    renderChips(picks); // Render the selected ingredients as clickable chip buttons
}

// Render API results from the backend into the assistant panel.
// The backend returns a plain JSON object, and this function turns that object
// into a user-facing message plus a list of clickable chips.
// Structural complexity is low because this render step only maps data to UI;
// it does not own auth, fetch, or database work.
function render(data) {
    const title = data.recipe_title || "a recipe you liked"; // Fall back to a generic phrase if no title is present
    const items = Array.isArray(data.suggested_ingredients) ? data.suggested_ingredients : []; // Guarantee an array

    if (data.no_favorites) {
        // If the user has not saved anything yet, the assistant explains that
        // first instead of showing an empty or confusing state.
        setMessage("Save a favorite recipe first, then I can suggest ingredients."); // Prompt the user to save a favorite first
    } else {
        // When favorites exist, the message connects the suggestions back to
        // the user's own saved recipe so the experience feels personal.
        setMessage("Since you liked " + title + ", try adding these:"); // Personalized message referencing the user's saved recipe
    }
    renderChips(items); // Display the suggested ingredients as clickable chip buttons
}

// Fetch ingredient suggestions for the signed-in user.
// This function is the bridge between the UI and the authenticated backend.
// Security lives in the token check here because the request must carry the
// current user's Firebase ID token before personalized data is returned.
async function loadData() {
    if (!user) {
        // Security: if we do not have a signed-in user yet, we stop before
        // making a request that would fail or return the wrong data.
        setMessage("Please log in first."); // Prompt the user to sign in
        chips.innerHTML = "";               // Clear any stale chip content
        return;
    }

    // Reliability: clear the panel and show a loading message so the user knows
    // the assistant is working instead of leaving stale chips on the screen.
    setMessage("Thinking about your favorites..."); // Show a loading indicator in the message area
    chips.innerHTML = ""; // Clear any previous chip content while the request is in flight

    // The backend requires a Firebase ID token, so we ask Firebase for the
    // current user's token right before the request.
    const token = await user.getIdToken(); // Request a fresh Firebase ID token for the current user

    // Send the token in the Authorization header so the API can verify access
    // and return only the current user's personalized suggestions.
    const response = await fetch("/api/ingredient-suggestions", {
        headers: { Authorization: "Bearer " + token }, // Attach the ID token for server-side auth
    });

    if (!response.ok) {
        // Reliability: if the API fails, we show a safe error message and clear
        // the chip area so the panel does not keep misleading old content.
        // This keeps the failure mode obvious instead of silently showing stale UI.
        setMessage("Could not load suggestions."); // Show a user-friendly error message
        chips.innerHTML = "";                      // Remove any stale chips so the state is clean
        return;
    }

    // The response is JSON, so we pass it into the renderer and let the UI
    // convert backend data into buttons and text.
    render(await response.json()); // Parse the JSON body and hand it to the render function
}

// Keep track of the current Firebase auth user so requests can be authorized.
// This callback stays in sync with the login state across the whole page.
onAuthStateChanged(auth, (firebaseUser) => {
    user = firebaseUser; // Update the module-level user reference on every auth state change
});

// Toggle the assistant panel and load personalized suggestions when opened.
// The panel loads data only when the user explicitly opens it, which keeps the
// page light and avoids unnecessary requests.
bubble.addEventListener("click", async () => {
    if (card.classList.contains("open")) { // If the panel is already open, close it instead
        closeCard(); // Hide the panel
        return;
    }

    openCard();       // Show the panel
    await loadData(); // Fetch and render personalized ingredient suggestions
});

// Show the random ingredient prompt and make each suggestion clickable.
// This is the "surprise me" path for a user who wants inspiration without
// waiting for backend data.
luckyBtn.addEventListener("click", () => {
    openCard();          // Ensure the panel is visible before populating it
    randomIngredients(); // Populate the panel with a random set of ingredient chips
});

// Close the panel when the user clicks outside it.
// This is standard UI cleanup so the assistant does not stay open forever.
document.addEventListener("click", (event) => {
    if (!card.classList.contains("open")) { // If the panel is not open, there is nothing to close
        return;
    }

    // Ignore clicks that happen inside the panel itself or on the bubble button.
    if (card.contains(event.target) || bubble.contains(event.target)) { // Click was inside the panel or on the toggle button
        return;
    }

    closeCard(); // The click was outside the panel and button — close the panel
});
