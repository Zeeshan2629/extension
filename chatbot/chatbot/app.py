# chatbot/app.py
import os
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import (
    LoginManager, login_user, login_required, logout_user, current_user
)
from dotenv import load_dotenv
from sqlalchemy import distinct

# === Chatbot imports ===
from loader import extract_text_from_pdf
from embedder import chunk_text, embed_chunks
from vector_store import VectorStore
from rag import answer_question

# === Load environment variables ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(BASE_DIR, ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(dotenv_path=ENV_PATH)

# === Initialize Flask app ===
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "test")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# === Security & DB Config ===
app.config["SECRET_KEY"] = "super-secret-key"  # change this before deployment
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chatbot.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ Import db + models
from models import db, User, ChatMessage
db.init_app(app)

# Enable non-blocking SQLite writes
@app.before_request
def set_sqlite_mode():
    try:
        db.session.execute("PRAGMA journal_mode=WAL;")
        db.session.execute("PRAGMA synchronous = NORMAL;")
    except Exception as e:
        app.logger.debug(f"SQLite mode setup skipped: {e}")

# === Flask-Login setup ===
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ======================================
# 🔐 AUTH ROUTES
# ======================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not username or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


# ======================================
# 🤖 CHATBOT CORE
# ======================================

# In-memory cache for indexed PDFs
DOCUMENT_STORES = {}


@app.route("/")
@login_required
def index():
    """Main chat interface (requires login)."""
    return render_template("index.html", username=current_user.username)


@app.route("/upload", methods=["POST"])
@login_required
def upload_file():
    """Handles PDF uploads and builds embeddings."""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    save_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(save_path)

    # 1️⃣ Extract text
    text = extract_text_from_pdf(save_path)

    # 2️⃣ Chunk text
    chunks = chunk_text(text, max_length=800)

    # 3️⃣ Embed chunks
    embeddings = embed_chunks(chunks)
    dim = embeddings.shape[1]

    # 4️⃣ Create vector store
    store = VectorStore(embedding_dim=dim)
    store.add(chunks, embeddings)

    # 5️⃣ Save to in-memory dictionary
    DOCUMENT_STORES[file.filename] = {"store": store, "chunks": chunks}

    return jsonify({
        "message": f"File {file.filename} uploaded and indexed successfully!",
        "filename": file.filename,
        "chunk_count": len(chunks),
        "preview": text[:800]
    })


# ======================================
# 💬 FIXED CHAT ROUTE
# ======================================
# ======================================
# 💬 FIXED CHAT ROUTE — Instant Response + Async DB Save
# ======================================
import threading

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    """Handles chatbot Q&A requests — instant output without refresh."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    filename = data.get("filename")
    question = data.get("question", "").strip()

    if not filename or filename not in DOCUMENT_STORES:
        return jsonify({"error": "Unknown filename. Upload and index the PDF first."}), 400
    if not question:
        return jsonify({"error": "Question is empty."}), 400

    start_time = time.time()
    store = DOCUMENT_STORES[filename]["store"]

    try:
        # === Generate Answer (main task)
        result = answer_question(question, store, top_k=3)
        answer = result.get("answer", "")
        context_used = result.get("context_used", [])

        # === Save Chat Messages Asynchronously ===
        def save_chat_async(user_id, filename, question, answer):
            with app.app_context():
                try:
                    user_msg = ChatMessage(
                        user_id=user_id,
                        filename=filename,
                        role="user",
                        message=question
                    )
                    bot_msg = ChatMessage(
                        user_id=user_id,
                        filename=filename,
                        role="assistant",
                        message=answer
                    )
                    db.session.add_all([user_msg, bot_msg])
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f"Background DB save failed: {e}")

        threading.Thread(
            target=save_chat_async,
            args=(current_user.id, filename, question, answer),
            daemon=True
        ).start()

        # === Return answer immediately (no waiting for DB)
        elapsed = round(time.time() - start_time, 2)
        response = jsonify({
            "answer": answer,
            "context_used": context_used,
            "elapsed_time": elapsed
        })
        response.headers["Cache-Control"] = "no-store"
        response.headers["Connection"] = "close"

        print(f"✅ Responded instantly in {elapsed}s")
        return response, 200

    except Exception as e:
        app.logger.exception(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500



# ======================================
# 📁 USER FILES & HISTORY
# ======================================
@app.route("/user_files")
@login_required
def user_files():
    """Return list of unique PDF filenames for the logged-in user."""
    files = (
        db.session.query(distinct(ChatMessage.filename))
        .filter(ChatMessage.user_id == current_user.id)
        .all()
    )
    filenames = [f[0] for f in files if f[0]]
    return jsonify(filenames)


@app.route("/history/<filename>")
@login_required
def get_chat_history(filename):
    """Return previous chat messages for this user and specific file."""
    messages = (
        ChatMessage.query.filter_by(user_id=current_user.id, filename=filename)
        .order_by(ChatMessage.timestamp.asc())
        .all()
    )
    history = [
        {"role": m.role, "message": m.message, "timestamp": m.timestamp.isoformat()}
        for m in messages
    ]
    return jsonify(history)


# ======================================
# 🧩 DB INIT
# ======================================
_db_initialized = False


@app.before_request
def create_tables_once():
    global _db_initialized
    if not _db_initialized:
        with app.app_context():
            db.create_all()
            app.logger.info("✅ Database and tables created (if not exist).")
            _db_initialized = True


# ======================================
# 🚀 RUN APP
# ======================================
if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
