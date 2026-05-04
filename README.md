#  **ChefGPT**

**ChefGPT** is a full-stack recipe meal planner web application that generates recipes based on ingredients entered by the user. Instead of searching multiple websites for meal ideas, users simply input the ingredients they already have along with an optional budget, and ChefGPT returns 3 complete AI-generated meal suggestions with step-by-step cooking instructions.

ChefGPT helps reduce food waste, save time, and simplify meal planning.

---

### **Setup Instructions (Reviewer)**


1. Install Python

Make sure Python 3 is installed on your system.

*  Ingredient-based recipe generation powered by AI
*  Optional budget input to tailor additional ingredient suggestions
*  3 AI-generated meal suggestions per search
*  Expandable dropdown cards for each recipe with full instructions
*  Itemized list of ingredients you already have vs. ingredients to buy
*  Clean and responsive user interface

python --version

If Python is not installed, download it from:
https://www.python.org/downloads/

2. Install pytest and flask

pip install flask pytest groq

To execute all test cases, run:

pytest -v <optionally, test file name goes here; ex: tests/test_IngredientSuggestion.py>




---

##  **Installation & Setup**

### **1️ Prerequisites**

Make sure you have **Python** installed. To check, open PowerShell and run:

```powershell
py --version
```

If Python is not installed, download it from [python.org/downloads](https://python.org/downloads).
> ⚠️ During installation, make sure to check **"Add Python to PATH"**.

---

### **2️ Clone the Repository**

```powershell
git clone https://github.com/omieibih/ChefGPT-Group-E-.git
cd ChefGPT-Group-E-
```

---

### **3️ Install Required Dependencies**

All required packages are listed in `requirements.txt`. Install them by running:

```powershell
py -m pip install -r requirements.txt
```

The `requirements.txt` contains:

```
blinker==1.9.0
click==8.3.1
colorama==0.4.6
Flask==3.1.2
gunicorn==25.1.0
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.3
packaging==26.0
Werkzeug==3.1.5
groq
```

---

### **4️ Get Your Groq API Key**

ChefGPT uses the **Groq API** for AI-generated recipes. To get your free API key:

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Navigate to **API Keys** in the left sidebar
4. Click **Create API Key** and copy it

> ⚠️ Copy the key immediately — it will only be shown once.

---

### **5️ Set Your API Key**

Before running the app, set your Groq API key as an environment variable in PowerShell:

```powershell
$env:GROQ_API_KEY="your-groq-api-key-here"
```

> ⚠️ Replace `your-groq-api-key-here` with your actual key. This must be run **every time you open a new PowerShell window** before starting the app.

---

### **5.1 Firebase Admin Credentials (Required for Login/Favorites)**

ChefGPT uses Firebase Admin on the backend for token verification and favorites storage.

Use one of these options:

1. Preferred (no key file on disk):

```powershell
$env:FIREBASE_SERVICE_ACCOUNT_JSON='{"type":"service_account", ... }'
```

2. Local key file path:

```powershell
$env:FIREBASE_SERVICE_ACCOUNT_PATH="serviceAccountKey.json"
```

`serviceAccountKey.json` is ignored by git and should never be committed.

---

### **5.2 Firebase Setup After Cloning (Teammate Checklist)**

Use this checklist so auth and favorites work on a fresh clone.

1. Create your own Firebase project (or get access to the team project).
2. In Firebase Authentication, enable:
  - Email/Password
  - Google (if you plan to use Google Sign-In)
3. In Firestore Database, create the database.
4. Open `static/firebase-config.js` and replace the `firebaseConfig` object with your own Web App config from:
  - Firebase Console -> Project settings -> General -> Your apps -> Web app
5. Create a service account key from:
  - Firebase Console -> Project settings -> Service accounts -> Generate new private key
6. Set one backend credential environment variable before running:

```powershell
$env:FIREBASE_SERVICE_ACCOUNT_PATH="C:/path/to/your/firebase-service-account.json"
```

or

```powershell
$json = Get-Content -Raw "C:/path/to/your/firebase-service-account.json"
$env:FIREBASE_SERVICE_ACCOUNT_JSON = $json
```

7. For better security, restrict your Firebase Web API key in Google Cloud:
  - Restrict by HTTP referrers
  - Restrict to required APIs only
8. Run the app and verify:
  - `/login` allows sign-up/login
  - creating favorites succeeds
  - favorites appear in Firestore

---

### **6️ Run the Application**

```powershell
py app.py
```

Once running, open your browser and go to:

```
http://localhost:5000
```

---

### **Full Startup Sequence (Run These in Order Every Time)**

```powershell
py -m pip install -r requirements.txt
```
```powershell
$env:GROQ_API_KEY="your-groq-api-key-here"
```
```powershell
py app.py
```

---

##  **Usage Guidelines**

* Enter ingredients separated by commas
  * Example: `chicken, rice, garlic`
* Optionally enter a budget (numbers only)
  * Example: `20`
* Click the **Generate Recipes** button
* Click on any meal card to expand and view its full recipe and instructions

---

##  **Running Unit Tests**

ChefGPT includes a unit test suite to verify core functionality. To run tests, first install pytest:

```powershell
py -m pip install pytest
```

Then run:

```powershell
py -m pytest test_app.py -v
```

The tests cover:
* Home page loading correctly
* Results page blocking invalid requests
* AI returning exactly 3 meals with all required fields
* Correct behavior when no budget is provided
* Proper error handling when the API fails

---


### **Frontend**
* **HTML**
* **CSS**

### **Backend**
* **Python**
* **Flask**

### **AI**
* **Groq API** (LLaMA 3.3 70B model)

1. The user enters available ingredients into the input field.
2. The user optionally enters a budget for buying extra ingredients.
3. The Groq AI processes the input and generates 3 meal suggestions.
4. Each meal is displayed in a dropdown card with:
   - Ingredients the user already has
   - Additional ingredients to buy (with estimated prices)
   - Step-by-step cooking instructions


```
ChefGPT/
│
├── app.py
├── requirements.txt
├── templates/
│   ├── index.html
│   └── results.html
├── static/
│   └── style.css
└── README.md
```

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
*  User authentication and saved recipes
*  AI-generated recipe images

---

##  **Project Status**

 Active Development
