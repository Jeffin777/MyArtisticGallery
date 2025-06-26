# 🌸 My Artistic Gallery

> *A poetic journaling web app powered by AI — turn your everyday moments into timeless verses.*

---

## ✨ About the Project

**My Artistic Gallery** is a personal and expressive web app that allows users to share simple life experiences and receive poetic responses crafted by AI.  
Each moment is transformed into an artistic, emotionally resonant piece of writing and saved in the user's private collection.

Whether it's helping someone, watching the rain, or simply smiling at a stranger — your memories become soft verses through the power of **Sarvam AI**.

---

## 🛠️ Features

- 🖋️ Generate poems from simple user inputs (real-life moments)
- 🔐 Register & login securely with JWT authentication
- 💬 Personalized AI-generated poetic responses using Sarvam API
- 💾 Save your favorite poems to a private collection
- 🗂️ View your saved poetic gallery with timestamps
- 💖 Elegant, soft UI designed for emotional storytelling

---

## 💡 Tech Stack

### 🧠 Backend
- **FastAPI** – Python web framework
- **SQLAlchemy** – ORM for managing SQLite database
- **JWT (via python-jose)** – Authentication
- **Passlib** – Password hashing
- **SarvamAI SDK** – AI-powered poetic response generation
- **python-dotenv** – Securely manage environment variables

### 🎨 Frontend
- **HTML, CSS, JavaScript** – Clean and minimal poetic UI

---

## 🧾 Installation

### 📦 Prerequisites

- Python 3.8+
- Git (for cloning)
- Your Sarvam AI API key

### 🚀 Setup Instructions

```bash
# 1. Clone the repository
git clone https://github.com/your-username/my-artistic-gallery.git
cd my-artistic-gallery

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a `.env` file with:
# (DO NOT share this publicly)
SECRET_KEY=your_secret_key_here
SARVAM_API_KEY=your_sarvam_api_key_here

# 5. Run the server
uvicorn backend.main:app --reload
---->📁 Folder Structure
css
Copy
Edit
project/
│
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   └── ...
│
├── frontend/
│   ├── index.html
│   ├── chat.html
│   ├── login.html
│   └── ...
│
├── requirements.txt
├── .gitignore
└── README.md
🙏 Acknowledgements
❤️ Built as a fun project to blend creativity with code

🌟 Special thanks to Sarvam AI for the poetic LLM

🤖 Developed with guidance from ChatGPT (OpenAI)

📢 License
This project is open-source and free to use under the MIT License.

🌐 Connect with Me
If you enjoy this idea or want to collaborate, feel free to connect on LinkedIn.
www.linkedin.com/in/jeffinjosepanamkuttiyil