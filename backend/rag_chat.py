import os
import sys

import chromadb
from dotenv import load_dotenv
from google import genai


# ============================================================
# PROJECT PATH
# ============================================================

# This file is:
# backend/rag_chat.py

BACKEND_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_DIR = os.path.dirname(
    BACKEND_DIR
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

# Look for .env in the main project folder

ENV_FILE = os.path.join(
    PROJECT_DIR,
    ".env"
)

load_dotenv(
    ENV_FILE
)


# ============================================================
# GEMINI API KEY
# ============================================================

api_key = os.getenv(
    "GEMINI_API_KEY"
)

if not api_key:

    raise ValueError(
        "GEMINI_API_KEY was not found. "
        "Please add GEMINI_API_KEY to your .env file."
    )


# ============================================================
# CONNECT TO GEMINI
# ============================================================

client_gemini = genai.Client(
    api_key=api_key
)


# ============================================================
# CHROMA DATABASE PATH
# ============================================================

# ChromaDB will be stored in the main project folder:
#
# Bharat-Darshan/
#     chroma_db/
#
# This works even when Streamlit is started using:
#
# streamlit run frontend/app.py

CHROMA_PATH = os.path.join(
    PROJECT_DIR,
    "chroma_db"
)


# ============================================================
# CONNECT TO CHROMADB
# ============================================================

client_chroma = chromadb.PersistentClient(
    path=CHROMA_PATH
)


# ============================================================
# GET HISTORY COLLECTION
# ============================================================

try:

    collection = client_chroma.get_collection(
        name="ancient_bharat"
    )

except Exception as e:

    raise RuntimeError(
        "\n\n"
        "ChromaDB collection 'ancient_bharat' was not found.\n\n"
        "Make sure your ChromaDB knowledge base has been "
        "created before running the application.\n\n"
        f"Expected ChromaDB location:\n{CHROMA_PATH}\n\n"
        f"Original error:\n{e}"
    )


# ============================================================
# HISTORY CHATBOT
# ============================================================

def ask_history_bot(question):

    # ========================================================
    # STEP 1: RETRIEVE RELEVANT INFORMATION
    # ========================================================

    results = collection.query(
        query_texts=[question],
        n_results=3
    )


    # ========================================================
    # CHECK WHETHER DOCUMENTS WERE FOUND
    # ========================================================

    documents = results.get(
        "documents",
        []
    )


    if (
        not documents
        or not documents[0]
    ):

        context = ""


    else:

        context = "\n\n".join(
            documents[0]
        )


    # ========================================================
    # STEP 2: CREATE PROMPT
    # ========================================================

    prompt = f"""
You are Bharat Darshan, an assistant that explains Ancient Indian history
and Hindu religious traditions in a clear, respectful, and educational way.

Use the following retrieved context to answer the user's question.

If the answer is not available in the context, clearly say:

"I don't currently have enough information about this topic in my curated knowledge base."

Do not invent historical facts.

RETRIEVED CONTEXT:
{context}

USER QUESTION:
{question}

Answer clearly and accurately.

Your answer should be based only on the retrieved context.
If the retrieved context does not contain enough information,
say that you do not currently have enough information in the
curated knowledge base.
"""


    # ========================================================
    # STEP 3: GENERATE ANSWER USING GEMINI
    # ========================================================

    response = client_gemini.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )


    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    return response.text


# ============================================================
# TEST THE RAG CHATBOT
# ============================================================

if __name__ == "__main__":

    question = (
        "Who was Ashoka and what happened "
        "after the Kalinga War?"
    )


    answer = ask_history_bot(
        question
    )


    print(
        "\nQUESTION:"
    )

    print(
        question
    )


    print(
        "\nBHARAT DARSHAN:"
    )

    print(
        answer
    )