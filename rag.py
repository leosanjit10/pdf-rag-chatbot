from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

base_dir = Path(__file__).resolve().parent
pdf_path = base_dir / "documents" / "sample.pdf"
vectorstore_path = base_dir / "vectorstore"

if not pdf_path.exists():
    raise FileNotFoundError(f"PDF not found: {pdf_path}")

# Load PDF
loader = PyPDFLoader(str(pdf_path))
docs = loader.load()

# Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
chunks = splitter.split_documents(docs)

# Create embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Create vector store
vectorstore = FAISS.from_documents(chunks, embeddings)

# Save locally
vectorstore.save_local(str(vectorstore_path))

print(f"Pages: {len(docs)}")
print(f"Chunks: {len(chunks)}")
print("FAISS index created successfully!")