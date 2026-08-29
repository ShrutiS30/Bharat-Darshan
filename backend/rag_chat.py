import os
import glob
import hashlib

import chromadb
from dotenv import load_dotenv
from google import genai


# ============================================================
# PROJECT PATHS
# ============================================================

# This file is:
# backend/rag_chat.py

BACKEND_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_DIR = os.path.dirname(
    BACKEND_DIR
)

DATA_DIR = os.path.join(
    PROJECT_DIR,
    "data"
)

CHROMA_PATH = os.path.join(
    PROJECT_DIR,
    "chroma_db"
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

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
        "Please add GEMINI_API_KEY to Streamlit Cloud Secrets."
    )


# ============================================================
# CONNECT TO GEMINI
# ============================================================

client_gemini = genai.Client(
    api_key=api_key
)


# ============================================================
# CONNECT TO CHROMADB
# ============================================================

client_chroma = chromadb.PersistentClient(
    path=CHROMA_PATH
)


# ============================================================
# GET OR CREATE KNOWLEDGE COLLECTION
# ============================================================

collection = client_chroma.get_or_create_collection(
    name="ancient_bharat"
)


# ============================================================
# TEXT FILE CHUNKING
# ============================================================

def split_text(
    text,
    chunk_size=1200,
    overlap=200
):

    text = text.strip()

    if not text:
        return []

    chunks = []

    start = 0

    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks


# ============================================================
# LOAD TEXT FILES INTO CHROMADB
# ============================================================

def load_knowledge_base():

    if not os.path.exists(DATA_DIR):
        return

    text_files = glob.glob(
        os.path.join(
            DATA_DIR,
            "*.txt"
        )
    )

    if not text_files:
        return

    # --------------------------------------------------------
    # Existing document IDs
    # --------------------------------------------------------

    try:

        existing = collection.get()

        existing_ids = set(
            existing.get(
                "ids",
                []
            )
        )

    except Exception:

        existing_ids = set()


    # --------------------------------------------------------
    # Process every TXT file
    # --------------------------------------------------------

    for file_path in text_files:

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                text = file.read()

        except Exception:

            continue


        chunks = split_text(
            text
        )


        # ----------------------------------------------------
        # Add each chunk
        # ----------------------------------------------------

        for index, chunk in enumerate(chunks):

            file_name = os.path.basename(
                file_path
            )

            unique_string = (
                file_name
                + "_"
                + str(index)
                + "_"
                + chunk
            )

            document_id = hashlib.md5(
                unique_string.encode(
                    "utf-8"
                )
            ).hexdigest()


            # -----------------------------------------------
            # Don't add duplicate chunks
            # -----------------------------------------------

            if document_id in existing_ids:
                continue


            try:

                collection.add(
                    ids=[
                        document_id
                    ],
                    documents=[
                        chunk
                    ],
                    metadatas=[
                        {
                            "source": file_name,
                            "chunk": index
                        }
                    ]
                )

                existing_ids.add(
                    document_id
                )

            except Exception:

                continue


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

load_knowledge_base()


# ============================================================
# HISTORY CHATBOT
# ============================================================

def ask_history_bot(question):

    question = question.strip()

    if not question:

        return (
            "Please enter a question about Ancient India."
        )


    # ========================================================
    # RETRIEVE RELEVANT INFORMATION
    # ========================================================

    try:

        results = collection.query(
            query_texts=[
                question
            ],
            n_results=3
        )

    except Exception as e:

        return (
            "I was unable to search the curated "
            "knowledge base at the moment."
        )


    # ========================================================
    # EXTRACT DOCUMENTS
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
    # CHECK KNOWLEDGE BASE
    # ========================================================

    if not context.strip():

        return (
            "I don't currently have enough information "
            "about this topic in my curated knowledge base."
        )


    # ========================================================
    # CREATE PROMPT
    # ========================================================

    prompt = f"""
You are Bharat Darshan, an assistant that explains Ancient Indian history
and Hindu religious traditions in a clear, respectful, and educational way.

Use ONLY the retrieved context below to answer the user's question.

Do not invent historical facts.

If the answer cannot be supported by the retrieved context, clearly say:

"I don't currently have enough information about this topic in my curated knowledge base."

RETRIEVED CONTEXT:
{context}

USER QUESTION:
{question}

Answer clearly and accurately.

Your answer must be based only on the retrieved context.
"""


    # ========================================================
    # GENERATE ANSWER USING GEMINI
    # ========================================================

    try:

        response = client_gemini.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

    except Exception:

        return (
            "I was unable to generate a response right now. "
            "Please try again."
        )


    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    if response.text:

        return response.text

    return (
        "I was unable to generate a response."
    )


# ============================================================
# LOCAL TEST
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
