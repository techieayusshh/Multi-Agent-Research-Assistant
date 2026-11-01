import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)
logger = logging.getLogger(__name__)


def answer_question(question, context):
    if not context.strip():
        raise ValueError("Cannot answer a document question without retrieved context.")

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=[
                {
                    "role": "user",
                    "content": f"""
You are an expert Research Assistant.

Answer ONLY using the information provided below.

Rules:
- Use only the provided text.
- Do not use outside knowledge.
- Cite sources using [1], [2], [3], etc.
- Match citation numbers to the corresponding [Source X] sections.
- Include citations for factual statements.
- Do not invent citations.
- If information comes from multiple sources, cite all relevant sources.
- If the answer is not present in the text, reply exactly:
"I couldn't find this information in the provided documents."

TEXT:
{context}

QUESTION:
{question}

ANSWER:
"""
                }
            ],
            temperature=0,
            max_tokens=600,
        )

        answer = response.choices[0].message.content.strip()
        logger.info("Generated grounded answer for document question")
        return answer

    except Exception as e:
        logger.exception("Document question agent failed")
        return f"❌ API Error: {e}"


def summarize_document(text):
    if not text.strip():
        raise ValueError("Cannot summarize an empty document.")

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=[
                {
                    "role": "user",
                    "content": f"""
You are an expert Research Assistant.

Summarize the research paper using only the provided text.

Provide:
1. Main Objective
2. Methodology
3. Key Findings
4. Conclusion

TEXT:
{text}

SUMMARY:
"""
                }
            ],
            temperature=0,
            max_tokens=800,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.exception("Summarization agent failed")
        return f"❌ API Error: {e}"


def general_answer(question):
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.3,
            max_tokens=600,

        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.exception("General knowledge agent failed")
        return f"❌ API Error: {e}"