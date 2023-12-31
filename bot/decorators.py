"""
This module defines function decorators for functions used in the main Telegram
Bot program (bot.py).

Function Decorators:
    restricted(func)
"""

import json
import os
from functools import wraps
from telegram import Update
from telegram.ext import (
    ContextTypes,
)

LIST_OF_ADMINS = json.loads(os.environ["LIST_OF_ADMINS"])


def restricted(func):
    """
    Restricts the usage of a python-telegram-bot handler to user IDs in
    LIST_OF_ADMINS.

    Args:
        func: A telegram.ext Handler object with at least the update and context
                  as arguments.

    Returns:
        A telegram.ext Handler object that only runs when called by a user in
        LIST_OF_ADMINS.

    Usage Example:
        In bot.py:
            @restricted
            async def start(update: Update,
                            context: ContextTypes.DEFAULT_TYPE) -> None:):
                ...
    """

    @wraps(func)
    async def wrapped(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            await update.message.reply_text(
                "You do not have permission to use this bot.",
                message_thread_id=update.message.message_thread_id,
            )
            return

        return await func(update, context, *args, **kwargs)

    return wrapped
