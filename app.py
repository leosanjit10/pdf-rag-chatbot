from query import ask_question


def main():
    while True:
        question = input("\nAsk a question (or type 'exit'): ").strip()

        if not question or question.lower() == "exit":
            break

        try:
            result = ask_question(question)
        except Exception as exc:
            print(f"\nError: {exc}")
            continue

        answer = result.get("answer") or result.get("result", "")

        print("\nAnswer:\n")
        print(answer)

        source_documents = result.get("source_documents", [])
        if source_documents:
            print("\nSources:\n")
            for index, doc in enumerate(source_documents, start=1):
                source = doc.metadata.get("source", f"Document {index}")
                page = doc.metadata.get("page")
                label = source
                if page is not None:
                    label = f"{label} (page {page})"

                print(f"{index}. {label}")
                print(doc.page_content[:400].replace("\n", " "))
                print("-" * 50)


if __name__ == "__main__":
    main()