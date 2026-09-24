from pathlib import Path
from typing import IO, Union

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
VECTORSTORE_PATH = BASE_DIR / "vectorstore"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def _sanitize_filename(filename: str) -> str:
    safe_name = (filename or "uploaded.pdf").strip()
    if not safe_name:
        safe_name = "uploaded.pdf"
    return Path(safe_name).name or "uploaded.pdf"


def _save_uploaded_pdf(pdf_file, target_name: str | None = None) -> Path:
    target_name = target_name or getattr(pdf_file, "name", "uploaded.pdf")
    target_path = BASE_DIR / "documents" / _sanitize_filename(target_name)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    pdf_file.seek(0)
    target_path.write_bytes(pdf_file.read())
    return target_path


def build_vector_store(
    pdf_source: Union[str, Path, IO[bytes], None] = None,
    save_name: str | None = None,
):
    if pdf_source is None:
        pdf_path = BASE_DIR / "documents" / "sample.pdf"
    elif hasattr(pdf_source, "read"):
        pdf_path = _save_uploaded_pdf(pdf_source, save_name)
    else:
        pdf_path = Path(pdf_source)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    VECTORSTORE_PATH.mkdir(parents=True, exist_ok=True)

    loader = PyPDFLoader(str(pdf_path))
    docs = loader.load()
    if not docs:
        raise ValueError(f"No readable pages were found in '{pdf_path}'.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(str(VECTORSTORE_PATH))

    result = {
        "pdf_path": str(pdf_path),
        "pages": len(docs),
        "chunks": len(chunks),
        "vectorstore_path": str(VECTORSTORE_PATH),
        "embedding_model": EMBEDDING_MODEL,
        "file_size": pdf_path.stat().st_size,
    }

    print(f"Pages: {len(docs)}")
    print(f"Chunks: {len(chunks)}")
    print(f"FAISS index created successfully at: {VECTORSTORE_PATH}")
    return result


if __name__ == "__main__":
    build_vector_store(BASE_DIR / "documents" / "sample.pdf")