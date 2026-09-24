# PDF RAG Chatbot

An AI-powered Retrieval-Augmented Generation (RAG) chatbot that enables users to upload PDF documents and ask questions about their content using semantic search and large language models.

## 🚀 Demo

Live Demo: https://pdf-rag-chatbot-ffav7ulz59q2o2tmzsz2zv.streamlit.app/

> Deploying on Streamlit Community Cloud

---

## 📸 Project Screenshot

<img width="1912" height="861" alt="image" src="https://github.com/user-attachments/assets/64082bb9-d320-45fc-aebf-02f634983a6c" />

<img width="1896" height="852" alt="image" src="https://github.com/user-attachments/assets/38d6496d-f26e-4ed4-969f-bc4125ebf5ed" />


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
git clone https://github.com/leosanjit10/pdf-rag-chatbot.git
cd pdf-rag-chatbot
```


### 2. Create a Virtual Environment

```bash
python -m venv
