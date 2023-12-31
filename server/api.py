"""
This Flask program contains API endpoints that allow the Telegram Bot to
interact with the database.

Routes:
    /get-question [GET]
    /insert-into-answer-log [POST]
    /get-user-stats [GET]
"""

import datetime
import logging
import random
from flask import Flask, request
import db

app = Flask(__name__)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Create database tables if they don't exist
db.create_tables()


@app.route("/get-question", methods=["GET"])
def get_new_question():
    """
    Randomly selects a question ID, queries the database for the question with
    the selected question ID, and returns the question.

    This function is called when a GET request to /get-question is made.

    URL Parameters:
        None

    Returns:
        A tuple containing:
            - A dictionary containing the properties of the selected question,
                  as the response content, and
            - The HTTP response status code 200.
    """

    no_of_questions = len(db.get_questions())

    if no_of_questions == 0:
        return ("There are no questions in the database", 400)

    question_id = random.randint(1, no_of_questions)
    question = db.select_question_by_id(question_id)

    return (
        {
            "id": question["id"],
            "text": question["text"],
            "answer": question["answer"],
            "remarks": question["remarks"],
        },
        200,
    )


@app.route("/insert-into-answer-log", methods=["POST"])
def new_user_answer():
    """
    Adds a user's quiz answer to the 'answer_log' table in the
    database.

    This function is called when a POST request to /insert-into-answer-log is
    made.

    URL Parameters:
        None
    Form Parameters:
        user_id: The Telegram user ID of the user that answered the quiz.
        user_answer: The quiz option that the user chose.
        question_id: The question ID of the quiz question that the user
                         answered.
    Returns:
        A tuple containing:
            - "The answer log has been updated" as the response content, and
            - the HTTP response status code 201.
    """

    user_id = request.form["user_id"]
    user_answer = request.form["user_answer"]
    question_id = request.form["question_id"]

    db.insert_into_answer_log(
        datetime.datetime.now(), user_id, user_answer, question_id
    )

    return ("The answer log has been updated.", 201)


@app.route("/get-user-stats", methods=["GET"])
def get_user_stats():
    """
    Queries the database for data regarding user answers to
    generate and return a list containing user answer statistics.

    This function is called when a GET request to /get-user-stats is made.

    URL Parameters:
        None

    Returns:
        A tuple containing:
            - A list containing user answer statistics, sorted in descending
                  order based on the percentage of questions answered correctly,
                  as the response content, and
            - the HTTP response status code 200.
    """

    questions = db.get_questions()
    answers = {}
    for question in questions:
        answers[question["id"]] = question["answer"]

    answer_log = db.get_answer_log()
    user_stats = {}
    for answer_event in answer_log:
        user_id = answer_event["user_id"]
        user_answer = answer_event["user_answer"]
        question_id = answer_event["question_id"]

        if user_id not in user_stats:
            user_stats[user_id] = {
                "user_id": user_id,
                "correctly_answered": 0,
                "wrongly_answered": 0,
                "total_answered": 0,
            }

        user_stats[user_id]["total_answered"] += 1

        correct_answer = answers[question_id]
        if user_answer == correct_answer:
            user_stats[user_id]["correctly_answered"] += 1
        else:
            user_stats[user_id]["wrongly_answered"] += 1

    for user_id, stats in user_stats.items():
        try:
            stats["percentage_correct"] = (
                stats["correctly_answered"] / stats["total_answered"] * 100
            )
        except ZeroDivisionError:
            stats["percentage_correct"] = 0

    user_stats_values = list(user_stats.values())
    user_stats_values.sort(key=lambda x: x["percentage_correct"], reverse=True)

    return (user_stats_values, 200)
