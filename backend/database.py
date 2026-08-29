import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "bharat_darshan.db")


def get_connection():
    return sqlite3.connect(DB_NAME)


def current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (chat_id) REFERENCES chats(id)
        )
    """)

    conn.commit()
    conn.close()


def get_or_create_user(email):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE email = ?",
        (email,)
    )

    row = cursor.fetchone()

    if row:
        user_id = row[0]

    else:
        cursor.execute(
            """
            INSERT INTO users (email, created_at)
            VALUES (?, ?)
            """,
            (
                email,
                current_timestamp()
            )
        )

        user_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return user_id


def create_chat(user_id, title):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chats
        (user_id, title, created_at)
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            title,
            current_timestamp()
        )
    )

    chat_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return chat_id


def save_message(chat_id, role, content):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO messages
        (chat_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            chat_id,
            role,
            content,
            current_timestamp()
        )
    )

    conn.commit()
    conn.close()


def get_all_chats(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, created_at
        FROM chats
        WHERE user_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (user_id,)
    )

    chats = cursor.fetchall()

    conn.close()

    return chats


def get_messages(chat_id, user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT m.role, m.content
        FROM messages m
        INNER JOIN chats c
            ON m.chat_id = c.id
        WHERE m.chat_id = ?
        AND c.user_id = ?
        ORDER BY m.id ASC
        """,
        (
            chat_id,
            user_id
        )
    )

    messages = cursor.fetchall()

    conn.close()

    return messages


def delete_chat(chat_id, user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM chats
        WHERE id = ?
        AND user_id = ?
        """,
        (
            chat_id,
            user_id
        )
    )

    conn.commit()
    conn.close()