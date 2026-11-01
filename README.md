# Inquiro

An AI-powered multi-agent research assistant for searching uploaded papers, generating grounded answers with page-level citations, summarizing documents, and answering unrelated general-knowledge questions.

**Status:** Available to run locally.

## Features

- Upload one or more research papers in PDF format.
- Extract text, split it into overlapping chunks, and index it with FAISS.
- Route document questions to a RAG agent with retrieved source context.
- Route summarization requests to a document summarization agent.
- Route unrelated questions to a General Knowledge agent.
- Inspect retrieved passages, source filenames, and exact page references.
- Clear uploaded PDFs, the local vector index, or the chat from the sidebar.

## How it works

1. `PyPDFLoader` extracts text and page metadata from uploaded PDFs.
2. Reference and bibliography pages are skipped. Remaining text is split into 600-character chunks with 100-character overlap.
3. `sentence-transformers/all-MiniLM-L6-v2` converts chunks to vectors stored in a local FAISS index.
4. The router selects `RAG`, `SUMMARY`, or `GENERAL` based on the request and whether documents are indexed.
5. For a document question, FAISS retrieves the three closest chunks. The RAG agent receives those chunks with numbered source markers and must ground factual claims in them.
6. Empty or low-relevance retrieval is reported explicitly instead of silently falling back to General Knowledge.

Summary requests use the full extracted text from the PDFs and do not use vector search. Questions unrelated to the uploaded corpus use the General Knowledge agent.

## Requirements

- Python 3.10 or newer
- An [OpenRouter API key](https://openrouter.ai/keys)
- Internet access on first run to download the embedding model and call OpenRouter

The first PDF upload may take a while because the embedding model is downloaded locally. CPU inference works, though indexing can be faster with suitable hardware.

## Run locally

Clone the repository and enter its directory:

```bash
git clone https://github.com/techieayusshh/DeepResearch-Agent.git
cd DeepResearch-Agent
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a `.env` file in the project root and add your own OpenRouter key:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
```

Keep `.env` private. It is excluded from Git by `.gitignore`; do not commit API keys.

Start the app:

```bash
streamlit run streamlit_app.py
```

Open the local URL printed by Streamlit, usually <http://localhost:8501>.

## Use the app

1. Upload one or more PDFs from the sidebar. Inquiro saves them under `data/` and builds the FAISS index under `vectorstore/`.
2. Ask a question about the papers, for example: "What methodology does the paper propose?"
3. Review the RAG answer's citations and expand **View Retrieved Document Passages** to inspect the exact chunks used.
4. Start a summary request with "Summarize..." or "Summary..." to summarize the complete document corpus.
5. Ask an unrelated question to use the General Knowledge agent.
6. Use **Purge DB** to remove the local PDFs and index, or **Clear Chat** to clear the conversation.

## Project layout

```text
streamlit_app.py       Inquiro Streamlit user interface and request flow
agents.py              OpenRouter calls for paper QA, summaries, and general answers
router.py              Selects the RAG, summary, or general agent
create_vector_db.py    PDF loading, chunking, embedding, and FAISS index creation
retriever.py           Loads the saved FAISS index
requirements.txt       Python dependencies
.env.example           Example OpenRouter environment variable
Result Output/         Application screenshots
```

Runtime folders `data/` and `vectorstore/` are created by the app and excluded from Git.

## Configuration and notes

- The chat model is `meta-llama/llama-3.3-70b-instruct` through OpenRouter.
- The embedding model is `sentence-transformers/all-MiniLM-L6-v2`.
- The app retrieves up to three chunks for paper questions and logs indexing, retrieval, and agent-selection diagnostics.
- Scanned PDFs without extractable text may need OCR before upload.
- Summary requests send the combined extracted PDF text to the model. Very large collections may exceed model context limits.
- General Knowledge answers are model generated and may be inaccurate; verify important information.

## Troubleshooting

**The app reports an API error:** Check that `.env` is in the project root, `OPENROUTER_API_KEY` is spelled correctly, and the key has access or credits on OpenRouter. Restart Streamlit after changing the key.

**PDF questions are not answered:** Confirm that the PDF contains selectable text and that indexing completed. Check the retrieved passages and application logs; Inquiro reports empty or low-relevance retrieval instead of switching silently to General Knowledge.

**The first upload is slow:** The embedding model is downloaded the first time and the PDF is indexed. Later runs can reuse the local model cache and saved index.

## Inquiro screenshots

The screenshots below show the current Inquiro interface, document RAG workflow, grounded answer, and page-level citation tracking.

![Inquiro document question and grounded answer](./Result%20Output/Inquiro-Paper-QA.png)

![Inquiro verified citations and retrieved passages](./Result%20Output/Inquiro-Citations.png)


## Contributing

Contributions are welcome. Fork the repository, create a branch for your change, and open a pull request with a clear description.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Author

**Ayush Raj** - [GitHub](https://github.com/techieayusshh)
