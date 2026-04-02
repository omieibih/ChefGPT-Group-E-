#  **ChefGPT**

**ChefGPT** is a full-stack recipe meal planner web application that generates recipes based on ingredients entered by the user. Instead of searching multiple websites for meal ideas, users simply input the ingredients they already have, and ChefGPT returns a complete recipe with step-by-step cooking instructions.

ChefGPT helps reduce food waste, save time, and simplify meal planning.

---

### **Setup Instructions (Reviewer)**


1. Install Python

Make sure Python 3 is installed on your system.

Check with:

python --version

If Python is not installed, download it from:
https://www.python.org/downloads/

2. Install Required Packages

Run the following command in the project directory:

pip install flask pytest

Running Unit Tests

To execute all test cases, run:

pytest -v <optionally, test file name goes here; ex: tests/test_IngredientSuggestion.py>

Alternatively, you can run:

python run_tests.py


---

##  **Installation & Setup**

### **1️ Clone the Repository**

```bash
git clone https://github.com/omieibih/ChefGPT-Group-E-.git
cd chefgpt
```

---

### **2️ Install Firebase CLI (If Needed)**

```bash
npm install -g firebase-tools
```

---

### **3️ Configure Firebase**

1. Go to the Firebase Console.

2. Create a new project.

3. Enable:

   * Authentication (optional)
   * Firestore Database
   * Hosting

4. Create a file named `firebase-config.js` and add:

```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "XXXX",
  appId: "XXXX"
};

firebase.initializeApp(firebaseConfig);
```

---

### **4️ Run the Application**

**Option 1:**
Open `index.html` directly in your browser.

**Option 2 (Firebase Hosting):**

```bash
firebase login
firebase init
firebase serve
```

---


##  **Usage Guidelines**

* Enter ingredients separated by commas

  * Example: `chicken, rice, garlic`
* Click the **Generate Recipe** button.
* Review the generated recipe.
* Save the recipe (if logged in).

---

##  **Contribution Guidelines**

1. Fork the repository.
2. Create a new branch:

```bash
git checkout -b feature-name
```

3. Commit your changes:

```bash
git commit -m "Add feature description"
```

4. Push to your branch:

```bash
git push origin feature-name
```

5. Submit a Pull Request.

---

##  **Authors**

* Ana Moron Cervantes
* Opeoluwa Orisadahunsi
* Favour Aloziem
* Nicholas Watson
* Jason Vo
* RJ Cortez
* Omieibi Harcourt

---

##  **Features**

*  Ingredient-based recipe generation
*  Step-by-step cooking instructions
*  Clean and responsive user interface
*  Firebase backend integration
*  User authentication (if implemented)
*  Save and retrieve recipes

---

##  **Tech Stack**

### **Frontend**

* **HTML**
* **CSS**
* **Python**

### **Backend / Cloud Services**

* **Firebase Authentication**
* **Firebase Firestore**
* **Firebase Hosting**
* **Gemini API**

---

##  **How It Works**

1. The user enters available ingredients into the input field.
2. The application processes the ingredients.
3. A matching recipe is generated.
4. The recipe is displayed with cooking instructions.
5. An image is generated.
6. (Features in progress): The recipe can be saved to the user's account.

---

##  **Project Structure**

```
ChefGPT/
│
├── index.html
├── style.css
├── script.js
├── firebase-config.js
└── README.md
```
---

##  **Future Improvements**

*  Nutrition and calorie tracking
*  Grocery list generator
*  Cuisine filtering
*  Weekly meal planning dashboard
*  AI-enhanced recipe recommendations

---

##  **Project Status**

 Active Development
