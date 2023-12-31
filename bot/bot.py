"""
This program starts the Telegram Bot when run.

The functions defined in this program are called when a user interacts with the
Telegram Bot.

The user input required to invoke a function call is configured by adding
handlers in main().

Functions:
    start(update, context)
    new_quiz(update, context)
    send_quiz(context)
    get_schedule(update, context)
    remove_quiz(update, context)
    show_leaderboard(update, context)
    receive_quiz_answer(update, context)
    main()
"""

from datetime import datetime
import logging
import os
import pytz
import requests
from telegram import Poll
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    Defaults,
    PollAnswerHandler,
)
from decorators import restricted
from utils import escape_markdownv2, format_quiz_remarks

FLASK_API_URL = os.environ["FLASK_API_URL"]
LOCAL_TIMEZONE = os.environ["LOCAL_TIMEZONE"]
RULES_PAGE_URL = os.environ["RULES_PAGE_URL"]
TELEGRAM_BOT_API_TOKEN = os.environ["TELEGRAM_BOT_API_TOKEN"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Logging level for "httpx" is set to "WARNING" to prevent logging of "httpx"
# messages during normal operation.
logging.getLogger("httpx").setLevel(logging.WARNING)


@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # pylint: disable=unused-argument
    """
    Sends a reply message indicating that the bot is running.

    This function is restricted to being invoked by a user in "LIST_OF_ADMINS".

    Args:
        update: A python-telegram-bot Update object that represents the incoming
                    update.
        context: A python-telegram-bot Context object that represents the
                    context for the incoming update.

    Returns:
        None
    """

    await update.message.reply_text(
        "DiscQuiz is running.", message_thread_id=update.message.message_thread_id
    )


@restricted
async def new_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Adds a 'send_quiz' job to the job queue.

    This job will call the send_quiz function at the time specified by the user.

    This function is restricted to being invoked by a user in "LIST_OF_ADMINS".

    Args:
        update: A python-telegram-bot Update object that represents the incoming
                    update.
        context: A python-telegram-bot Context object that represents the
                    context for the incoming update.

    Returns:
        None
    """

    if len(context.args) < 1:
        await update.message.reply_text(
            "Please specify a time for the quiz to be sent.",
            message_thread_id=update.message.message_thread_id,
        )
    else:
        if "active_quiz_message_id" not in context.bot_data:
            context.bot_data.update({"active_quiz_message_id": None})
        try:
            new_quiz_time = datetime.strptime(context.args[0], "%H:%M")
        except ValueError:
            await update.message.reply_text(
                "Invalid time format. Please specify the time in the HH:MM format.",
                message_thread_id=update.message.message_thread_id,
            )
        else:
            quiz_time_is_invalid = False
            scheduled_jobs = context.job_queue.jobs()
            for job in scheduled_jobs:
                if job.data["time_to_send"] == new_quiz_time:
                    quiz_time_is_invalid = True
                    break

            if quiz_time_is_invalid:
                await update.message.reply_text(
                    "There is already a daily quiz scheduled for "
                    f"{new_quiz_time.strftime('%H:%M')}.",
                    message_thread_id=update.message.message_thread_id,
                )
            else:
                context.job_queue.run_daily(
                    send_quiz,
                    new_quiz_time,
                    chat_id=update.message.chat_id,
                    data={
                        "message_thread_id": update.message.message_thread_id,
                        "time_to_send": new_quiz_time,
                    },
                )
                await update.message.reply_text(
                    "You have scheduled a quiz to be sent at "
                    f"{new_quiz_time.strftime('%H:%M')} daily.",
                    message_thread_id=update.message.message_thread_id,
                )


async def send_quiz(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Stops the current quiz, if it exists, and sends a new quiz to the chat.

    This function runs when a 'send_quiz' job in the job queue runs.

    Args:
        update: A python-telegram-bot Update object that represents the incoming
                    update.
        context: A python-telegram-bot Context object that represents the
                    context for the incoming update.

    Returns:
        None
    """

    if context.bot_data["active_quiz_message_id"] is not None:
        # If there is an existing quiz
        await context.bot.stop_poll(
            chat_id=context.job.chat_id,
            message_id=context.bot_data["active_quiz_message_id"],
        )

    response = requests.get(f"{FLASK_API_URL}/get-question", timeout=3)

    match response.status_code:
        case 200:
            response_data = response.json()

            question_id = response_data["id"]
            question_text = response_data["text"]
            answer = response_data["answer"]
            remarks = response_data["remarks"]

            context.bot_data.update({"active_quiz_question_id": question_id})

            newly_created_quiz = await context.bot.send_poll(
                chat_id=context.job.chat_id,
                message_thread_id=context.job.data["message_thread_id"],
                type=Poll.QUIZ,
                is_anonymous=False,
                question=question_text,
                options=["True", "False"],
                correct_option_id=0 if answer == "TRUE" else 1,
                explanation=format_quiz_remarks(remarks, RULES_PAGE_URL),
                explanation_parse_mode="MarkdownV2",
            )

            context.bot_data.update(
                {"active_quiz_message_id": newly_created_quiz.message_id}
            )
        case _:
            logging.error(response.text)


@restricted
async def get_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends a reply message containing a list of the times of the currently
    scheduled daily quizzes.

    This function is restricted to being invoked by a user in "LIST_OF_ADMINS".

    Args:
        update: A python-telegram-bot Update object that represents the incoming
                    update.
        context: A python-telegram-bot Context object that represents the
                    context for the incoming update.

    Returns:
        None
    """

    schedule = []
    scheduled_jobs = context.job_queue.jobs()
    for job in scheduled_jobs:
        schedule.append(job.data["time_to_send"])

    schedule.sort()

    if len(schedule) == 0:
        await update.message.reply_text(
            "There are no scheduled quizzes.",
            message_thread_id=update.message.message_thread_id,
        )
    else:
        bot_reply_message = "__Daily Schedule__\n"
        for quiz_time in schedule:
            bot_reply_message += f"•{quiz_time.strftime('%H:%M')}\n"

        await update.message.reply_text(
            bot_reply_message,
            message_thread_id=update.message.message_thread_id,
            parse_mode="MarkdownV2",
        )


@restricted
async def remove_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Removes a 'send_quiz' job from the job queue.

    The 'send_quiz' job that will be removed is the one with the time that
    matches the time specified by the user.

    This function is restricted to being invoked by a user in "LIST_OF_ADMINS".

    Args:
        update: A python-telegram-bot Update object that represents the incoming
                    update.
        context: A python-telegram-bot Context object that represents the
                    context for the incoming update.

    Returns:
        None
    """

    if len(context.args) == 0:
        await update.message.reply_text(
            "Please specify the time of the quiz to be removed.",
            message_thread_id=update.message.message_thread_id,
        )
    else:
        try:
            quiz_time_to_remove = datetime.strptime(context.args[0], "%H:%M")
        except ValueError:
            await update.message.reply_text(
                "Invalid time format. Please specify the time in the HH:MM format.",
                message_thread_id=update.message.message_thread_id,
            )
        else:
            scheduled_jobs = context.job_queue.jobs()
            quiz_was_removed = False
            for job in scheduled_jobs:
                if job.data["time_to_send"] == quiz_time_to_remove:
                    job.schedule_removal()
                    quiz_was_removed = True
                    break

            if quiz_was_removed:
                await update.message.reply_text(
                    "The daily quiz scheduled for "
                    f"{quiz_time_to_remove.strftime('%H:%M')} has been removed.",
                    message_thread_id=update.message.message_thread_id,
                )
            else:
                await update.message.reply_text(
                    "There is no daily quiz scheduled for "
                    f"{quiz_time_to_remove.strftime('%H:%M')}.",
                    message_thread_id=update.message.message_thread_id,
                )


@restricted
async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends a reply message containing the current leaderboard.

    This function is restricted to being invoked by a user in "LIST_OF_ADMINS".

    Args:
        update: A python-telegram-bot Update object that represents the incoming
                    update.
        context: A python-telegram-bot Context object that represents the
                    context for the incoming update.

    Returns:
        None
    """

    response = requests.get(f"{FLASK_API_URL}/get-user-stats", timeout=3)

    match response.status_code:
        case 200:
            response_data = response.json()
            bot_reply_message = "__Leaderboard__\n"
            leaderboard_position = 1
            for user in response_data:
                user_obj = await context.bot.get_chat(user["user_id"])
                username = user_obj.username

                no_of_correctly_answered = user["correctly_answered"]
                total_answered = user["total_answered"]
                percentage_correct = str(round(user["percentage_correct"]))

                bot_reply_message += escape_markdownv2(
                    f"{leaderboard_position}. {username} - {percentage_correct}% "
                    f"({no_of_correctly_answered}/{total_answered})\n"
                )
                leaderboard_position += 1

            await update.message.reply_text(
                bot_reply_message,
                message_thread_id=update.message.message_thread_id,
                parse_mode="MarkdownV2",
            )
        case _:
            logging.error(response.text)


async def receive_quiz_answer(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Adds a user's quiz answer to the database by making a POST request to
    "/insert-into-answer-log".

    This function is run when a user answers a quiz sent by the bot.

    Args:
        update: A python-telegram-bot Update object that represents the incoming
                    update.
        context: A python-telegram-bot Context object that represents the
                    context for the incoming update.

    Returns:
        None
    """

    answer_obj = update.poll_answer
    user_id = answer_obj.user.id
    user_answer = "TRUE" if answer_obj.option_ids[0] == 0 else "FALSE"
    question_id = context.bot_data["active_quiz_question_id"]

    response = requests.post(
        f"{FLASK_API_URL}/insert-into-answer-log",
        data={
            "user_id": user_id,
            "user_answer": user_answer,
            "question_id": question_id,
        },
        timeout=3,
    )

    match response.status_code:
        case 201:
            pass
        case _:
            logging.error(response.text)


def main() -> None:
    """
    Creates, configures, and runs the bot.

    Args:
        None

    Returns:
        None
    """

    # Instantiate a Defaults object
    defaults = Defaults(tzinfo=pytz.timezone(LOCAL_TIMEZONE), quote=False)

    # Create the Application and pass it to the bot's token
    application = (
        ApplicationBuilder().token(TELEGRAM_BOT_API_TOKEN).defaults(defaults).build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("new", new_quiz))
    application.add_handler(CommandHandler("remove", remove_quiz))
    application.add_handler(CommandHandler("schedule", get_schedule))
    application.add_handler(CommandHandler("leaderboard", show_leaderboard))
    application.add_handler(PollAnswerHandler(receive_quiz_answer))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
