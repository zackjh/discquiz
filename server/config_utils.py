"""
This module contains a collection of functions that perform various tasks
required by the config.py program.

Functions:
    add_questions()
"""

import csv
import os
from wfdf_question_scraper import generate_csv_from_html
import db

CSV_FILE_PATH = "questions.csv"

def add_questions():
    """
    Adds questions to the 'questions' table in the database by providing the
    path to a HTML file of the WFDF Advanced Accreditation Quiz results page.

    A CSV file will be generated using data from the provided HTML file.

    This CSV file will subsequently be removed once all the questions have
    been added to the database.

    The name of this temporary CSV file is determined by the CSV_FILE_PATH
    variable at the top of this module.

    Args:
        None
    
    Returns:
        None
    """

    html_file_path = input("Enter the file path of the HTML file: ")
    print()

    try:
        with open(html_file_path, "r", encoding="utf-8") as html_file:
            raw_html = html_file.read()
            generate_csv_from_html(raw_html, CSV_FILE_PATH)
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"Error validating the HTML file {html_file_path}: {e}")
        return None

    try:
        with open(CSV_FILE_PATH, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file)

            # Skip headers in CSV file
            next(csv_reader)

            result = {
                "added": 0,
                "already_exists": 0,
                "too_long": 0,
            }

            for row in csv_reader:
                text = row[0]
                answer = row[1]
                remarks = row[2]

                if len(text) > 300:
                    # Question text is too long - Telegram polls have a 300
                    # character limit
                    result["too_long"] += 1
                elif db.select_question_by_text(text) is not None:
                    # Question already exists in the database
                    result["already_exists"] += 1
                else:
                    db.insert_into_question(text, answer, remarks)
                    result["added"] += 1

            # Remove the newly generated CSV file
            os.remove(CSV_FILE_PATH)
            print("Operation Complete")
            print(f"• {result["added"]} questions added")
            print(f"• {result["already_exists"]} questions not added as they "
                  "already exist in the database")
            print(f"• {result["too_long"]} questions not added as they contain "
                  "too many characters")
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"Error validating the CSV file: {e}")
        return None
