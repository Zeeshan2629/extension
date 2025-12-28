# AutoDoc AI Suite

### Developed by **Zeeshan Shaikh and team — MIT ADT University**

A unified AI-powered suite designed to help developers **understand code**, **visualize logic**, and **interact with documents intelligently**.
This suite combines **Code Analysis**, **Flowchart Generation**, **Documentation Generation**, and a **full PDF RAG Chatbot** into one cohesive system.

---

# 🚀 1. AutoDoc Code Analyzer

### (VS Code Extension Compatible Backend)

A powerful backend engine that provides:

### ✅ Flowchart Generation (PNG)

* Converts Python code → AST → Pseudocode → Flowchart
* Supports:

  * Conditionals
  * Loops
  * Functions
  * IO operations
  * Nested structures
* Rendered cleanly using Pillow (PIL)

### ✅ Documentation Generation (PDF)

* Analyzes Python source code
* Generates:

  * High-level summaries
  * Logic breakdown
  * Variable/Function explanations
  * Error identification
  * Optimization suggestions
* Output saved as a **professional PDF**

### Core Engine Components

* Python-to-pseudocode conversion
* Layout engine with binary tree logic
* Flowchart rendering engine
* PDF writer with structured document output
* CLI runner for easy usage

---

# 🤖 2. AutoDoc PDF Chatbot

### (Flask RAG Application)

A fully functional, modern PDF chatbot powered by a retrieval-based architecture.

### ✨ Features

* Upload & index PDFs
* Extract text automatically
* Chunk & embed documents
* Perform similarity search
* Chat with your documents
* Provide citations from source PDF
* Login/Register system
* Chat history saved per user per file
* Light/Dark theme
* Beautiful animated UI
* Sliding sidebar (mobile-friendly)

### Technical Pipeline

1. PDF → Text extraction
2. Text → Chunks
3. Chunks → Embeddings
4. Embeddings → Vector Store
5. Query → Similarity Search
6. Relevant Context → Response
7. Store chat history in database

### Storage

* SQLite database (`chatbot.db`)
* Contains:

  * `User` accounts
  * `ChatMessage` entries

---

# 🔗 3. Integrated AutoDoc Suite

Both systems complement each other, forming a **complete developer productivity ecosystem**.

| Component               | Purpose                                         |
| ----------------------- | ----------------------------------------------- |
| Code Analyzer           | Understand & visualize Python code              |
| Documentation Generator | Produce professional explanation PDFs           |
| PDF Chatbot             | Interact with documents through natural queries |

The suite is designed to evolve into a fully automated documentation + analysis platform.

---

# 🛠 Installation & Usage

### 1️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate # Linux/Mac
```

### 2️⃣ Install Requirements


### 3️⃣ Run the Chatbot App

```bash
python chatbot/app.py
```

Open in browser:

```
http://127.0.0.1:5000/
```

### 4️⃣ Generate Flowcharts

```bash
python flowchart_generator/run.py flowchart yourfile.py
```

### 5️⃣ Generate Documentation

```bash
python flowchart_generator/run.py doc yourfile.py
```

---

# 🌟 Future Enhancements

* Multi-PDF knowledge graphs
* AI-powered code reviewer
* Auto test-case generator
* Multi-file flowchart stitching
* GitHub integration
* Cloud vector storage
* ER diagram + architecture generator

---

# 🏆 Author

**Zeeshan Shaikh**
MIT ADT University


---


