import os
import logging

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


logger = logging.getLogger(__name__)


def create_vector_db(data_folder):
    documents = []

    # Load all PDFs
    for file in sorted(os.listdir(data_folder)):

        if file.endswith(".pdf"):

            pdf_path = os.path.join(data_folder, file)

            loader = PyPDFLoader(pdf_path)

            pages = loader.load()
            logger.info("Extracted %d pages from %s", len(pages), file)

            for page in pages:

                text = page.page_content

                # Skip reference/bibliography pages
                if (
                    "References" in text
                    or "REFERENCES" in text
                    or "Bibliography" in text
                    or "BIBLIOGRAPHY" in text
                ):
                    continue

                documents.append(page)

    if not documents:
        raise ValueError("No extractable text was found in the uploaded PDF files.")

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError("The uploaded PDF files did not contain usable text.")

    # Create embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Create FAISS vector database
    vector_db = FAISS.from_documents(
        chunks,
        embeddings
    )

    # Save locally
    vector_db.save_local("vectorstore")
    logger.info(
        "Created FAISS index: %d chunks, %d vectors, %d source documents",
        len(chunks),
        vector_db.index.ntotal,
        len({chunk.metadata.get("source") for chunk in chunks}),
    )

    return vector_db


if __name__ == "__main__":
    create_vector_db("data")