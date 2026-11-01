import logging

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


logger = logging.getLogger(__name__)


def get_retriever():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_db = FAISS.load_local(
        "vectorstore",
        embeddings,
        allow_dangerous_deserialization=True
    )

    logger.info(
        "Loaded FAISS index: %d vectors, %d documents",
        vector_db.index.ntotal,
        len(vector_db.docstore._dict),
    )

    return vector_db