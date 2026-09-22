# 🏋️ AI Fitness Assistant

A modern, full-stack AI-powered Fitness Assistant web application built with HTML, CSS, JavaScript, Python (Flask), SQLite, and Google Gemini AI integration.

---

## 📁 Project Structure

```
AI-Fitness-Assistant/
├── frontend/
│   ├── index.html       # Landing page with feature highlights
│   ├── login.html       # User Authentication (Login & Register)
│   ├── dashboard.html   # Main User Hub & quick stats
│   ├── chatbot.html     # AI Fitness Assistant Chat interface
│   ├── workout.html     # Interactive Workout Plan Generator
│   ├── nutrition.html   # Nutrition guide & Meal recommendations
│   ├── progress.html    # Weight & Workout history tracking
│   ├── style.css        # Responsive dark theme styling
│   └── script.js        # Dynamic UI logic & Flask API integration
│
├── backend/
│   ├── app.py           # Flask server entry point & API routes
│   ├── chatbot.py       # Gemini AI chat module with fallback logic
│   ├── workout.py       # Workout generator service
│   └── database.py      # SQLite database setup & CRUD logic
│
├── database/
│   └── fitness.db       # SQLite database (auto-generated)
│
├── .env                 # Environment configuration (API Keys)
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```

---

## 🌐 Website Flow

```text
Home (index.html)
  ↓
Login / Register (login.html)
  ↓
Dashboard (dashboard.html)
  ↓
 ┌───────────────┬──────────────┬──────────────┐
 ↓               ↓              ↓              ↓
AI Chatbot    Workout        Nutrition      Progress
(chatbot.html)(workout.html)(nutrition.html)(progress.html)
```

---

## ✨ Features

1. **🤖 AI Chatbot**: Ask fitness, diet, and training questions. Powered by Google Gemini AI with fallback response capabilities.
2. **🏋️ Workout Generator**: Custom routine builder based on fitness goal (Muscle Gain, Weight Loss, Endurance, Flexibility) and experience level (Beginner, Intermediate, Advanced).
3. **🍎 Nutrition Planner**: Meal suggestions, macronutrient guides, and calorie/protein calculation info.
4. **📊 Progress Tracker**: Track weight logs over time, log workouts, and view historical progress statistics.
5. **🔐 User Authentication**: Local authentication backed by SQLite database and browser session storage.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- A Google Gemini API Key (optional, but recommended for AI features). Get one free at [Google AI Studio](https://aistudio.google.com/).

### 2. Installation & Setup

```bash
# Clone or navigate into project directory
cd AI-Fitness-Assistant

# Create a virtual environment (optional but recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Open `.env` and insert your Gemini API Key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key
```

### 4. Run the Application

```bash
python backend/app.py
```

Open your browser and navigate to:
👉 `http://127.0.0.1:5000`

---

## 🛠️ Technology Stack
- **Frontend**: HTML5, CSS3 (Glassmorphism Dark UI), Vanilla JavaScript (Fetch API)
- **Backend**: Python, Flask, Flask-CORS
- **AI**: Google Gemini AI (`google-generativeai`)
- **Database**: SQLite3
