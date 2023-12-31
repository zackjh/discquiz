"""
This program provides a CLI for managing quiz questions in the database.
"""

from config_utils import add_questions
import db

# Create database tables if they don't exist
db.create_tables()


# Continue running the program until the user chooses to exit
while True:
    print("\n" + "=" * 40)
    print("OPTIONS".center(40))
    print("=" * 40 + "\n")
    print("1. Add new questions")
    print("2. Exit")
    print("\n" + "=" * 40)

    user_choice = input("\nEnter your choice: ")

    print("\n" + "=" * 40 + "\n")

    if user_choice == "1":
        add_questions()
    elif user_choice == "2":
        print("Exiting the program. Goodbye!")
        print("\n" + "=" * 40)
        break
    else:
        print("Invalid choice. Please try again.\n")
