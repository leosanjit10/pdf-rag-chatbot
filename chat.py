from pathlib import Path
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_classic.chains import RetrievalQA

# Load API key
load_dotenv()

# Paths
base_dir = Path(__file__).resolve().parent
vectorstore_path = base_dir / "vectorstore"

# Load embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

# Load vector store
vectorstore = FAISS.load_local(
    str(vectorstore_path),
    embeddings,
    allow_dangerous_deserialization=True
)

# Create retriever
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}
)

# Load LLM
llm = ChatGroq(
    model_name="openai/gpt-oss-20b"
)

# Create QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

# Chat loop
while True:
    question = input("\nAsk a question (or type 'exit'): ")

    if question.lower() == "exit":
        break

    result = qa_chain.invoke({"query": question})

    print("\nAnswer:\n")
    print(result["result"])

    print("\nSources:\n")
    for doc in result["source_documents"]:
        print(doc.page_content[:300])
        print("-" * 50)