"""
This module contains a collection of functions that perform CRUD operations
on a SQLite database.

Functions:
    connect_to_db()
    create_tables()
    insert_into_question(text, answer, remarks)
    select_question_by_text(text)
    select_question_by_id(question_id)
    get_questions()
    insert_into_answer_log(timestamp, user_id, user_answer, question_id)
    get_answer_log()
"""

import os
import sqlite3

DATABASE_PATH = os.environ["DATABASE_PATH"]


def connect_to_db():
    """
    Creates a connection the database and returns that connection.

    Args:
        None

    Returns:
        A sqlite3 Connection object that connects to the database.
    """

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    """
    Creates the 'questions' and 'answer_log' tables if they don't exist.

    Args:
        None

    Returns:
        None
    """

    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(
        """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                text TEXT NOT NULL,
                answer TEXT NOT NULL,
                remarks TEXT
            )
        """
    )
    cur.execute(
        """
            CREATE TABLE IF NOT EXISTS answer_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                timestamp DATE NOT NULL,
                user_id INTEGER NOT NULL,
                user_answer INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                FOREIGN KEY(question_id) REFERENCES questions(id)
            )
        """
    )
    conn.commit()
    conn.close()


def insert_into_question(text, answer, remarks):
    """
    Inserts a record into the 'questions' table.

    Args:
        text: A string of the question text.
        answer: A string of the correct answer to the question.
        remarks: A string of the question remarks.

    Returns:
        None
    """

    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(
        """
            INSERT INTO questions(text, answer, remarks)
            VALUES (?, ?, ?)
        """,
        (text, answer, remarks),
    )
    conn.commit()
    conn.close()


def select_question_by_text(text):
    """
    Selects and returns the record in the 'questions' table which has the
    matching 'text'.

    Args:
        text: A string of the question text of the question record that should
                  be returned.

    Returns:
        A sqlite3 Row object that contains the question with the specified
        'text'.
    """

    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(
        """
            SELECT *
            FROM questions
            WHERE text = ?
        """,
        (text,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def select_question_by_id(question_id):
    """
    Selects and returns the record in the 'questions' table which has the
    matching 'id'.

    Args:
        text: A string of the question ID of the question record that should
                  be returned.

    Returns:
        A sqlite3 Row object that contains the question with the specified 'id'.
    """

    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(
        """
            SELECT *
            FROM questions
            WHERE id = ?
        """,
        (question_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_questions():
    """
    Selects and returns all records in the 'questions' table.

    Args:
        None

    Returns:
        A list of sqlite3 Row objects, with each Row object representing a
        question.
    """

    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(
        """
            SELECT *
            FROM questions
        """,
    )
    rows = cur.fetchall()
    return rows


def insert_into_answer_log(timestamp, user_id, user_answer, question_id):
    """
    Inserts a record into the 'answer_log' table.

    Args:
        text: A string of the question text.
        answer: A string of the correct answer to the question.
        remarks: A string of the question remarks.

        timestamp: A date object that represents the time at which the user
                       answered the quiz.
        user_id: A string of the Telegram user ID of the user who answered the
                     quiz.
        user_answer: A string of the quiz option that the user chose.
        question_id: The question ID of the quiz question that the user
                         answered.

    Returns:
        None
    """

    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(
        """
            INSERT INTO answer_log(timestamp, user_id, user_answer, question_id)
            VALUES (?, ?, ?, ?)
        """,
        (timestamp, user_id, user_answer, question_id),
    )
    conn.commit()
    conn.close()


def get_answer_log():
    """
    Selects and returns all records in the 'answer_log' table.

    Args:
        None

    Returns:
        A list of sqlite3 Row objects, with each Row object representing a
        user answer.
    """

    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(
        """
            SELECT *
            FROM answer_log
        """
    )
    rows = cur.fetchall()
    return rows
