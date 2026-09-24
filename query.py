import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_groq import ChatGroq
except ImportError as exc:
    raise RuntimeError(
        "Missing LangChain dependencies. Install them with: pip install -r requirements.txt"
    ) from exc

try:
    from langchain_classic.chains import RetrievalQA
except ImportError:
    try:
        from langchain.chains.retrieval_qa.base import RetrievalQA
    except ImportError as exc:
        raise RuntimeError(
            "Neither langchain_classic nor langchain.chains is available. "
            "Install a compatible LangChain version."
        ) from exc

_qa_chain = None


def _get_vectorstore_path() -> Path:
    return Path(__file__).resolve().parent / "vectorstore"


def reset_qa_chain():
    global _qa_chain
    _qa_chain = None


def _build_qa_chain():
    vectorstore_path = _get_vectorstore_path()

    if not (vectorstore_path / "index.faiss").exists():
        raise FileNotFoundError(
            "Vector store not found. Upload and process a PDF in Streamlit first."
        )

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set. Add it to your environment or .env file.")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local(
        str(vectorstore_path),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=api_key,
        temperature=0,
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
    )


def get_qa_chain():
    global _qa_chain
    if _qa_chain is None:
        _qa_chain = _build_qa_chain()
    return _qa_chain


def ask_question(question: str):
    result = get_qa_chain().invoke({"query": question})
    answer = result.get("result") or result.get("answer") or ""
    return {
        "answer": answer,
        "result": answer,
        "source_documents": result.get("source_documents", []),
    }


__all__ = ["ask_question", "get_qa_chain", "reset_qa_chain"]