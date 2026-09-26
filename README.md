# 🤖 Nexa AI

Nexa AI is a professional AI chatbot application built with **FastAPI, Python, MySQL, and OpenRouter**.

It provides intelligent conversations, user authentication, chat history, cross-chat memory, and image understanding in a clean and modern interface.

## ✨ Features

* 💬 AI-powered conversations
* 🧠 Cross-chat memory
* 🗂️ Chat history
* 🔐 User signup and login
* 👤 User-specific conversations
* 🖼️ Image upload and image-based questions
* 🌙 Dark and light mode
* 📝 Markdown support
* 💻 Code highlighting and code copy
* ⚡ FastAPI backend
* 🗄️ MySQL database
* 🎨 Professional responsive UI

## 🧠 GenAI Features

Nexa AI uses an LLM through the OpenRouter API and includes:

* System prompt engineering
* Conversation context management
* Temperature and Top-P control
* User memory
* Multimodal image understanding
* Basic AI tool integration

## 🛠️ Tech Stack

### Backend

* Python
* FastAPI
* Uvicorn

### AI

* OpenRouter API
* Large Language Models
* Multimodal Vision Model

### Database

* MySQL

### Frontend

* HTML
* CSS
* JavaScript
* Jinja2

## 📁 Project Structure

```text
nexa_ai/
│
├── main.py
├── ai_model.py
├── prompts.py
├── context_manager.py
├── memory.py
├── vision.py
│
├── tools/
│   └── calculator.py
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   └── components/
│       └── attach_menu.html
│
├── static/
│   ├── css/
│   └── js/
│
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/thevimleshh/Nexa-AI.git
```

Go into the project folder:

```bash
cd Nexa-AI
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_api_key

MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=nexa_ai

SESSION_SECRET=your_secret_key
```

**Never upload your `.env` file or API keys to GitHub.**

## 🗄️ Database

Create a MySQL database named:

```sql
CREATE DATABASE nexa_ai;
```

Then create the required tables for:

* Users
* Conversations
* Messages
* Memories

## ▶️ Run the Application

Start the FastAPI server:

```bash
python -m uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## 📌 Project Status

Nexa AI is an ongoing GenAI project.

Future improvements may include:

* Better AI model routing
* Improved memory management
* Advanced multimodal capabilities
* AI evaluation
* Production deployment

## 👨‍💻 Author

**Vimlesh Yadav**

GitHub:
https://github.com/thevimleshh

---

⭐ If you find this project interesting, consider giving it a star!
