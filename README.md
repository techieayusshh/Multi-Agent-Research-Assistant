# Multi-Agent Research Assistant

Ask questions about research papers with a Streamlit app powered by retrieval-augmented generation (RAG). Upload PDFs, search their text with semantic retrieval, and get answers with page references. You can also ask general questions or request a structured summary of the uploaded papers.

**Status:** Available to run locally; no public demo is deployed yet.

## Features

- Upload one or more research papers in PDF format.
- Extract text, split it into overlapping chunks, and index it with FAISS.
- Ask questions about uploaded papers and see retrieved passages and page references.
- Automatically answer from general model knowledge when no PDFs are indexed or the closest search result is outside the app's relevance threshold.
- Request a summary with the headings Main Objective, Methodology, Key Findings, and Conclusion.
- Clear uploaded PDFs and the local vector index from the sidebar.

## How it works

1. `PyPDFLoader` extracts text and page metadata from uploaded PDFs.
2. Pages identified as references or bibliography are skipped. Remaining text is split into 600-character chunks with 100-character overlap.
3. The `sentence-transformers/all-MiniLM-L6-v2` embedding model converts chunks to vectors, which are stored in a local FAISS index.
4. For a paper question, the app retrieves the three closest chunks and asks the LLM to answer using those sources with citations.
5. If no index exists, or the closest result is beyond the configured distance threshold, the app uses the general-knowledge agent.

Summary requests use the full extracted text from the PDFs and do not use the vector search step. The current router recognizes requests that begin with `summarize`, `summarise`, or `summary`.

## Requirements

- Python 3.10 or newer
- An [OpenRouter API key](https://openrouter.ai/keys)
- Internet access on first run to download the embedding model and to call OpenRouter

The first PDF upload may take a while because the embedding model is downloaded locally. CPU inference works, though indexing can be faster with suitable hardware.

## Run locally

Clone the repository and enter its directory:

```bash
git clone https://github.com/techieayusshh/multi-agent-research-assistant-llm-langchain-faiss-rag.git
cd multi-agent-research-assistant-llm-langchain-faiss-rag
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

1. Upload one or more PDFs from the sidebar. The app saves the files under `data/` and builds the FAISS index under `vectorstore/`.
2. Ask a question about the papers, for example: “What methodology does the paper propose?”
3. Review the answer’s citations and expand **Retrieved Documents** to inspect the passages used.
4. Start a summary request with “Summarize…”, “Summarise…”, or “Summary…” to summarize the extracted text.
5. Ask a general question to use the general-knowledge agent. With no indexed PDFs, regular questions are sent directly to that agent.
6. Use **Clear Uploaded PDFs** to remove the local PDFs and index, or **Clear Chat** to clear the conversation.

## Project layout

```text
streamlit_app.py       Streamlit user interface and request flow
agents.py              OpenRouter calls for paper QA, summaries, and general answers
router.py              Detects summary requests
create_vector_db.py    PDF loading, chunking, embedding, and FAISS index creation
retriever.py           Loads the saved FAISS index
requirements.txt       Python dependencies
.env.example           Example OpenRouter environment variable
Result Output/         Application screenshots
```

Runtime folders `data/` and `vectorstore/` are created by the app and are excluded from Git.

## Configuration and notes

- The chat model is `meta-llama/llama-3.3-70b-instruct` through OpenRouter.
- The embedding model is `sentence-transformers/all-MiniLM-L6-v2`.
- The app retrieves up to three chunks for paper questions. The relevance cutoff is set in `streamlit_app.py`.
- Scanned PDFs without extractable text may need OCR before upload.
- Summary requests send the combined extracted PDF text to the model. Very large collections may exceed the model's context limits.
- General-knowledge answers are model generated and may be inaccurate; verify important information.

## Troubleshooting

**The app reports an API error:** Check that `.env` is in the project root, `OPENROUTER_API_KEY` is spelled correctly, and the key has access/credits on OpenRouter. Restart Streamlit after changing the key.

**PDF questions always use general knowledge:** Confirm that the PDF contains selectable text and that upload/indexing completed. Try asking a question that uses terms found in the paper.

**The first upload is slow:** The embedding model is downloaded the first time and the PDF must be indexed. Later runs can reuse the local model cache and saved index.

## Screenshots

| Uploading a paper | Paper Q&A |
|---|---|
| ![Uploading a research paper](./Result%20Output/Upload%20Research%20paper.png) | ![Paper question and answer](./Result%20Output/Rag%20Agent.png) |

| Summary | General knowledge |
|---|---|
| ![Document summary](./Result%20Output/Summarizer.png) | ![General knowledge answer](./Result%20Output/General%20Agent.png) |

![Application interface](./Result%20Output/Interface.png)

## Contributing

Contributions are welcome. Fork the repository, create a branch for your change, and open a pull request with a clear description.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Author

**Ayush Raj** · [GitHub](https://github.com/techieayusshh)
