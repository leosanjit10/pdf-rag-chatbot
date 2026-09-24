# PDF RAG Chatbot

An AI-powered Retrieval-Augmented Generation (RAG) chatbot that enables users to upload PDF documents and ask questions about their content using semantic search and large language models.

## 🚀 Demo

Live Demo: https://pdf-rag-chatbot-ffav7ulz59q2o2tmzsz2zv.streamlit.app/

> Deploying on Streamlit Community Cloud

---

## 📸 Project Screenshot

screenshots/chatbot.png

> Add a screenshot of your application by creating a `screenshots` folder and saving your image as `chatbot.png`.

---

## ✨ Features

- Upload PDF documents
- Extract and process PDF content
- Ask natural language questions about documents
- Retrieval-Augmented Generation (RAG)
- Semantic search with vector embeddings
- Fast document retrieval using FAISS
- Groq LLM integration
- Interactive Streamlit user interface
- Chat history support
- Clean and responsive design

---

## 🛠️ Tech Stack

### Frontend
- Streamlit

### Backend
- Python
- LangChain

### Vector Database
- FAISS

### LLM
- Groq

### Embeddings
- Sentence Transformers

### Other Libraries
- PyPDF
- Python Dotenv

---

## 📂 Project Structure

```text
pdf-rag-chatbot/
│
├── streamlit_app.py
├── ingest.py
├── query.py
├── requirements.txt
├── README.md
├── .gitignore
├── screenshots/
│   └── chatbot.png
└── vectorstore/
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/pdf-rag-chatbot.git
cd pdf-rag-chatbot
```

### 2. Create a Virtual Environment

```bash
python -m venv
