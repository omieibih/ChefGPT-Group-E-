import { auth } from "/static/firebase-config.js";
import { onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";

// Cache the assistant UI elements so the script can update the panel without
// repeatedly querying the DOM.
const bubble = document.getElementById("assistant-toggle");
const card = document.getElementById("assistant-panel");
const text = document.getElementById("assistant-message");
const luckyBtn = document.getElementById("assistant-lucky");
const chips = document.getElementById("assistant-chips");
const input = document.getElementById("ingredients-input");

let user = null;

// A small pool of starter ingredients used when the user wants a random prompt.
const luckyPool = ["garlic", "onion", "tomato", "rice", "eggs", "chicken", "pasta", "beans", "carrot", "mushroom", "spinach", "potato"];

// Open and close the assistant panel.
function openCard() {
    card.classList.add("open");
}

function closeCard() {
    card.classList.remove("open");
}

// Read the ingredient input as a normalized array so we can compare values
// consistently and avoid duplicate entries.
function currentList() {
    return input.value
        .split(",")
        .map((item) => item.trim().toLowerCase())
        .filter(Boolean);
}

// Add a suggested ingredient into the input field if it is not already there.
function addItem(item) {
    const clean = item.trim();

    if (!clean) {
        return;
    }

    if (currentList().includes(clean.toLowerCase())) {
        return;
    }

    input.value = input.value.trim() === "" ? clean : input.value.trim() + ", " + clean;
}

// Build a small random set of ingredients and render them as clickable chips.
function randomIngredients() {
    const picks = [];

    while (picks.length < 3 && picks.length < luckyPool.length) {
        const item = luckyPool[Math.floor(Math.random() * luckyPool.length)];
        if (!picks.includes(item)) {
            picks.push(item);
        }
    }

    text.textContent = "I'm feeling lucky, try these random ingredients:";
    chips.innerHTML = "";

    for (const item of picks) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "assistant-chip";
        button.textContent = item;
        button.addEventListener("click", () => addItem(item));
        chips.appendChild(button);
    }
}

// Render API results from the backend into the assistant panel.
function render(data) {
    const title = data.recipe_title || "a recipe you liked";
    const items = Array.isArray(data.suggested_ingredients) ? data.suggested_ingredients : [];

    if (data.no_favorites) {
        text.textContent = "Save a favorite recipe first, then I can suggest ingredients.";
    } else {
        text.textContent = "Since you liked " + title + ", try adding these:";
    }
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

// Fetch ingredient suggestions for the signed-in user.
async function loadData() {
    if (!user) {
        text.textContent = "Please log in first.";
        chips.innerHTML = "";
        return;
    }

    const token = await user.getIdToken();
    const response = await fetch("/api/ingredient-suggestions", {
        headers: { Authorization: "Bearer " + token },
    });

    if (!response.ok) {
        text.textContent = "Could not load suggestions.";
        chips.innerHTML = "";
        return;
    }

    render(await response.json());
}

// Keep track of the current Firebase auth user so requests can be authorized.
onAuthStateChanged(auth, (firebaseUser) => {
    user = firebaseUser;
});

// Toggle the assistant panel and load personalized suggestions when opened.
bubble.addEventListener("click", async () => {
    if (card.classList.contains("open")) {
        closeCard();
        return;
    }

    openCard();
    await loadData();
});

// Show the random ingredient prompt and make each suggestion clickable.
luckyBtn.addEventListener("click", () => {
    openCard();
    randomIngredients();
});
