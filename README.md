# Bharat Darshan

 ## Live Demo

[Visit Bharat Darshan](https://bharat-darshan-kkinhyd6t8ybimsrz2kdbt.streamlit.app/)
## AI-Powered Explorer of Ancient Indian History

Bharat Darshan is an AI-powered conversational application designed to help users explore the history, culture, traditions, and heritage of Ancient India through an interactive chat experience.

The application combines Retrieval-Augmented Generation (RAG) with Google Gemini to provide answers based on a curated knowledge base rather than relying entirely on the language model's general knowledge.

---

## Features

- AI-powered conversational interface
- Curated knowledge base on Ancient Indian history
- Retrieval-Augmented Generation (RAG)
- Context-aware answers using ChromaDB
- Email-based user login
- Personalized chat history for each user
- Multiple conversations with separate chat histories
- Delete individual conversations
- Information on Ancient Indian history and traditions
- Historical-themed user interface
- Interactive Streamlit interface

---

## Project Architecture

```text
Bharat-Darshan/
│
├── frontend/
│   ├── app.py
│   └── temple_background.jpg
│
├── backend/
│   ├── __init__.py
│   ├── database.py
│   └── rag_chat.py
│
├── data/
│   └── *.txt
│
├── chroma_db/
│
├── ingest.py
├── requirements.txt
├── .gitignore
└── README.md
