import { auth } from "/static/firebase-config.js";
import { onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";

const bubble = document.getElementById("assistant-toggle");
const card = document.getElementById("assistant-panel");
const text = document.getElementById("assistant-message");
const luckyBtn = document.getElementById("assistant-lucky");
const chips = document.getElementById("assistant-chips");
const input = document.getElementById("ingredients-input");

let user = null;

const luckyPool = ["garlic", "onion", "tomato", "rice", "eggs", "chicken", "pasta", "beans", "carrot", "mushroom", "spinach", "potato"];

function openCard() {
    card.classList.add("open");
}

function closeCard() {
    card.classList.remove("open");
}

function currentList() {
    return input.value
        .split(",")
        .map((item) => item.trim().toLowerCase())
        .filter(Boolean);
}

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

onAuthStateChanged(auth, (firebaseUser) => {
    user = firebaseUser;
});

bubble.addEventListener("click", async () => {
    if (card.classList.contains("open")) {
        closeCard();
        return;
    }

    openCard();
    await loadData();
});

luckyBtn.addEventListener("click", () => {
    openCard();
    randomIngredients();
});
