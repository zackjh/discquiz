"""
This module contains functions used to scrape the HTML of the WFDF Advanced
Accreditation Quiz results age.

The generate_csv_from_html function is the main function, while the remaining
functions serve as helper functions.

Functions:
    get_question_text(show_question_content_html_class)
    get_correct_answer(show_question_choices_html_class)
    get_remarks(watupro_main_feedback_html_class)
    generate_csv_from_html(raw_html, csv_file_path)
"""

import re
import csv
from bs4 import BeautifulSoup


def get_question_text(show_question_content_html_class):
    """
    Scrapes a HTML element with class="show-question-content" and returns the
    question text from that question.

    Args:
        show_question_content_html_class: A BS4 Tag object representing the
                                              HTML element with the
                                              class="show-question-content".

    Returns:
        A string of the question text from the specified question.
    """

    question_text = ""
    tags = show_question_content_html_class.find_all(class_="p1")

    for tag in tags:
        formatted_text = re.sub(r"\s+", " ", tag.text.strip())

        if tag.name == "li":
            bullet_point = "\u2022"
            question_text += f"{bullet_point} {formatted_text}"
        elif tag.name == "p":
            question_text += formatted_text
        else:
            raise TypeError

        question_text += "\n"

    return question_text.strip()


def get_correct_answer(show_question_choices_html_class):
    """
    Scrapes a HTML element with class="show-question-choices" and returns the
    correct answer from that question.

    Args:
        show_question_choices_html_class: A BS4 Tag object representing the HTML
                                              element with the
                                              class="show-question-choices".
    Returns:
        A string, either "TRUE" or "FALSE", of the correct answer of the
        specified question.
    """

    answer = (
        show_question_choices_html_class.find(class_="correct-answer")
        .find(class_="answer")
        .text
    )

    return "TRUE" if answer == "True" else "FALSE"


def get_remarks(watupro_main_feedback_html_class):
    """
    Scrapes a HTML element with class="watupro-main-feedback" and returns the
    remarks from that question.

    Args:
        watupro_main_feedback_html_class: A BS4 Tag object representing the HTML
                                              element with the
                                              class="watupro-main-feedback".

    Returns:
        A string of the remarks from the specified question.
    """

    remarks = watupro_main_feedback_html_class.find(class_="p1").text
    formatted_remarks = re.sub(r"\s+", " ", remarks.strip())

    return formatted_remarks


def generate_csv_from_html(raw_html, csv_file_path):
    """
    Scrapes the HTML of the WFDF Advanced Accreditation Quiz results page and
    generates a CSV file containing the quiz questions.

    Args:
        raw_html: A string containing the HTML of the results page.
        csv_file_path: The file path of the CSV file that will be generated.

    Returns:
        None
    """

    soup = BeautifulSoup(raw_html, "lxml")
    questions = soup.find_all(class_="watupro-choices-columns")

    data_to_write = []
    for question in questions:
        question_text = get_question_text(question.find(class_="show-question-content"))
        correct_answer = get_correct_answer(
            question.find(class_="show-question-choices")
        )
        remarks = get_remarks(question.find(class_="watupro-main-feedback"))

        data_to_write.append(
            {
                "question_text": question_text,
                "correct_answer": correct_answer,
                "remarks": remarks,
            }
        )

    # Define the headers for the CSV file
    headers = ["question_text", "correct_answer", "remarks"]

    with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
        csvwriter = csv.DictWriter(csv_file, fieldnames=headers)

        # Write headers to the CSV file
        csvwriter.writeheader()

        # Write each dictionary as a row in the CSV file
        for item in data_to_write:
            csvwriter.writerow(item)
