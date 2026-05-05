# 📡 Signal Challenge

**Signal Challenge** is a mobile quiz application designed for adaptive learning in **Telecommunications and Signal Processing**, powered by **Large Language Models (LLMs)**.

The application dynamically generates multiple-choice questions in real time, providing a **non-deterministic and continuously evolving learning experience**.

---

## 🚀 Features

- 📱 Cross-platform mobile app (React Native + Expo)
- 🧠 LLM-powered question generation (via OpenRouter API)
- 🎯 37 specialized topics in:
  - Telecommunications
  - Signal Processing
- 🎮 Gamified experience:
  - Score tracking
  - Immediate feedback
  - Progress indicators
- 🔀 Fully dynamic content:
  - No fixed question bank
  - New questions every session
- 🎚️ Three difficulty levels:
  - Foundational (Easy)
  - Advanced (Medium)
  - Expert (Hard)

---

## 🧠 Core Idea

Unlike traditional quiz platforms based on static question banks, Signal Challenge leverages the **stochastic nature of LLMs** to generate **unique questions at every interaction**.

This approach promotes:
- Continuous engagement
- Reduced memorization bias
- Broader conceptual exposure

---

## 🏗️ Architecture Overview

The application follows a **state-driven interaction model**:

1. **Menu**
2. **Loading (Question Generation)**
3. **Quiz**
4. **Results**

### Key Components

- `buildPrompt()` → Constructs structured prompts for the LLM  
- `requestQuestion()` → Handles API calls and JSON parsing  
- `shuffleOptions()` → Applies Fisher–Yates shuffle with correct answer tracking  
- Fallback mechanism → Ensures robustness in case of API failure  

---

## 🔌 API Integration

- **Provider:** OpenRouter  
- **Model:** `mistralai/mistral-large-2407`  
- **Temperature:** `0.2` (optimized for technical accuracy)

### Expected Response Format

```json
{
  "question": "string",
  "options": ["A", "B", "C", "D", "E"],
  "correct_index": 0
}
````

---

## 📚 Topics Covered

The app includes **37 topics** spanning:

### Communications & Networks

* Wireless Communications
* 5G / B5G / 6G
* Satellite Communications
* Internet of Things (IoT)
* Information Theory and Coding
* Cognitive Radio
* Cybersecurity
* ...and more

### Signal Processing

* Digital Signal Processing
* Image and Video Processing
* Audio and Speech Processing
* Graph Signal Processing
* Biomedical Signal Processing
* Sparse Representations
* ...and more

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/signal-challenge.git
cd signal-challenge
```

### 2. Install dependencies

```bash
npm install
```

### 3. Configure API Key

Open the main file and replace:

```javascript
const OPENROUTER_KEY = 'SUA_API_KEY_AQUI';
```

with your OpenRouter API key.

---

### 4. Run the app

```bash
npx expo start
```

---

## 🎮 How It Works

1. Select a difficulty level
2. The app generates **10 questions** dynamically
3. Each question:

   * Uses a random topic
   * Is generated via LLM API
4. Immediate feedback is provided after each answer
5. Final score is displayed at the end

---

## ⚠️ Limitations

* LLM-generated content may occasionally contain **hallucinations**
* No guarantee of 100% technical correctness
* Requires internet connection (API-based)

---

## 🔬 Research Context

This project is part of ongoing research in:

* AI-assisted education
* Adaptive learning systems
* LLM-based content generation

It has been proposed as a tool for engineering education in:

* Telecommunications
* Signal Processing

---

## 🔮 Future Work

* Human or AI-based validation layer for generated questions
* Explanation generation for answers
* Personalized learning paths
* User performance analytics
* Classroom-based experimental evaluation

---

## 📄 License

This project is for academic and research purposes.

---

## 👨‍💻 Author

**Vitor Amadeu Souza**
Electrical Engineering Professor & Researcher
Brazil

---

## ⭐ Acknowledgments

* OpenRouter API
* Mistral AI
* React Native & Expo ecosystem

---

## 📬 Contact

Feel free to open issues or contribute to the project.


