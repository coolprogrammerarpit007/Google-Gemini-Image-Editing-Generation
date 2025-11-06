🖼️ Gemini Image Editing API (FastAPI + MySQL)

A backend service built with FastAPI, MySQL (async), and Google Gemini Image Models for:

✅ AI Image Generation (Text → Image)

✅ AI Image Editing (Base64 Image + Text → Modified Image)

✅ Logging all requests in a database

✅ Serving generated images via static URLs

⚙️ Tech Stack

Python 3.11+ (3.13 supported)

FastAPI – web framework

SQLAlchemy (Async) – ORM

MySQL (via aiomysql / asyncmy) – Database

Pillow (PIL) – Image handling

Google Gemini (genai) – AI Image API

Uvicorn – ASGI Server

📁 Project Structure
ImageEditing/
│
├── app/
│ ├── main.py # FastAPI app entry point
│ ├── routes/
│ │ └── image_routes.py # API routes
│ ├── core/
│ │ ├── config.py # Environment + DB config
│ │ └── database.py # Async database connection
│ ├── models/
│ │ └── image_log.py # SQLAlchemy model
│ ├── schemas/
│ │ └── image_schema.py # Request & response schemas
│ ├── services/
│ │ └── gemini_service.py # Google Gemini integration
│ └── utils/
│ └── response_utils.py # Standardized API responses
│
├── generated_images/ # Stores AI-generated & edited images
├── .env # Environment variables
├── .venv/ # Python virtual environment
├── requirements.txt
└── README.md

🚀 Local Setup Guide
1️⃣ Clone the Repository
git clone https://github.com/yourusername/gemini-image-api.git
cd app

(or just open your folder if local)

2️⃣ Create & Activate Virtual Environment
python -m venv .venv

Windows:

.venv\Scripts\Activate.ps1

Linux/Mac:

source .venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure .env

Create a .env file in your project root directory (same level as app/):

GOOGLE_API_KEY=your_google_gemini_api_key
DB_USER=root
DB_PASS=
DB_HOST=localhost
DB_NAME=image_editing_gemini_db
SERVER_HOST=http://localhost:9000

💡 Make sure to create the database manually before running:

CREATE DATABASE image_editing_gemini_db;

5️⃣ Verify MySQL Async Driver Installed

For Python 3.13, prefer asyncmy (faster & more compatible):

pip install asyncmy

Then update your .env accordingly:

DATABASE_URL=mysql+asyncmy://root:@localhost:3306/image_editing_gemini_db

Otherwise, you can use aiomysql:

DATABASE_URL=mysql+aiomysql://root:@localhost:3306/image_editing_gemini_db

6️⃣ Run the Server

From the project root folder (not inside /app):

uvicorn app.main:app --reload --port 9000

✅ Server will start at:

http://localhost:9000

🧪 API Documentation (Swagger UI)

Once the server is running, open:

👉 http://localhost:9000/docs
