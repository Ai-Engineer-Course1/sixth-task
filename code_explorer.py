# mypy: ignore-errors
from __future__ import annotations

import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.vectorstores import LanceDB
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

SOURCE_DIR = Path(__file__).resolve().parent / "my-project"
LANCEDB_URI = Path(__file__).resolve().parent / "lancedb"
TABLE_NAME = "code_chunks"

EMBEDDING_MODEL = "all-minilm"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
RETRIEVER_K = 2

SYSTEM_PROMPT = (
    "You are a code exploration assistant. Use the `search_code` tool to find "
    "relevant snippets from the indexed Python source files before answering. "
    "Base every answer on the retrieved code and mention the file it came from. "
    "If the tool returns no relevant code, say so instead of guessing."
)


def load_source_documents(source_dir: Path) -> list[Document]:
    """Read every Python file in ``source_dir`` into LangChain documents."""
    documents: list[Document] = []
    for path in sorted(source_dir.glob("*.py")):
        documents.append(
            Document(
                page_content=path.read_text(encoding="utf-8"),
                metadata={"source": path.name},
            )
        )
    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    """Split documents with the Python-aware recursive text splitter."""
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(documents)


def build_retriever() -> VectorStoreRetriever:
    """Embed the source files and store them in a local LanceDB table."""
    table_path = LANCEDB_URI / f"{TABLE_NAME}.lance"
    if table_path.exists():
        shutil.rmtree(table_path)

    documents = load_source_documents(SOURCE_DIR)
    chunks = split_documents(documents)
    embeddings = OllamaEmbeddings(
        model=os.environ.get("OLLAMA_EMBEDDING_MODEL", EMBEDDING_MODEL)
    )

    vector_store = LanceDB.from_documents(
        chunks,
        embeddings,
        uri=str(LANCEDB_URI),
        table_name=TABLE_NAME,
    )
    return vector_store.as_retriever(search_kwargs={"k": RETRIEVER_K})


def build_agent(retriever: VectorStoreRetriever):
    """Create the LangChain agent with a retrieval tool."""

    @tool
    def search_code(query: str) -> str:
        """Search the indexed source code for snippets relevant to the question."""
        documents = retriever.invoke(query)
        if not documents:
            return "No relevant code found."
        return "\n\n".join(
            f"# {document.metadata.get('source', 'unknown')}\n{document.page_content}"
            for document in documents
        )

    model = ChatGoogleGenerativeAI(
        model=os.environ.get("GOOGLE_MODEL", "gemini-3.5-flash-lite"),
    )
    return create_agent(model, tools=[search_code], system_prompt=SYSTEM_PROMPT)


def message_text(message) -> str:
    """Extract plain text from a LangChain message that may use content blocks."""
    content = message.content
    if isinstance(content, str):
        return content
    parts: list[str] = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "\n".join(parts)


def main() -> None:
    load_dotenv()

    retriever = build_retriever()
    agent = build_agent(retriever)

    while True:
        question = input(
            "What do you want to know from the code? (or type 'exit' for exit)\n> "
        ).strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        result = agent.invoke({"messages": [{"role": "user", "content": question}]})
        print(f"\n{message_text(result['messages'][-1])}\n")


if __name__ == "__main__":
    main()
