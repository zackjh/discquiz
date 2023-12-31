"""
This module contains a collection of utility functions that perform various
tasks required by the main Telegram Bot program (bot.py).

Functions are added to this module (as opposed to being written in bot.py) when:
    - the task performed by the function is used repeatedly throughout bot.py,
          or
    - the code written to perform the function is lengthy and/or would make
          bot.py unnecessarily long and/or complex.

Functions:
    escape_markdownv2(input_string)
    format_quiz_remarks(text, rules_page_url)
"""

import re


def escape_markdownv2(input_string):
    # pylint: disable=anomalous-backslash-in-string
    """
    Escapes special characters in the input string for Telegram MarkdownV2
    compatibility.

    Args:
        input_string: The string that will be escaped.

    Returns:
        A string with "\" prepended to all special characters (as per the
        Telegram MarkdownV2 specification).

    Usage Example:
        >>> s = escape_markdownv2("1. zackjh - 80% (16/20)")
        >>> print(s)
        "1\. zackjh \- 80% \(16/20\)"
    """

    special_chars = [
        "_",
        "*",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]

    escaped_string = ""
    for char in input_string:
        if char in special_chars:
            escaped_string += "\\" + char
        else:
            escaped_string += char

    return escaped_string


def format_quiz_remarks(quiz_remarks_text, rules_page_url):
    # pylint: disable=anomalous-backslash-in-string
    """
    Formats quiz remarks by replacing WFDF rule numbers with hyperlinks and
    escaping the text for Telegram MarkdownV2 compatibility.

    Args:
        quiz_remarks_text: The string that will be formatted.
        rules_page_url: The URL of the webpage that the resulting hyperlinks
                            will point to.

    Returns:
        A string with:
            - All rule numbers replaced with the MarkdownV2 hyperlink
                  [{rule_number}]({rules_page_url}#rule_number), and
            - "\" prepended to all special characters (as per the Telegram
                  MarkdownV2 specification).

    Usage Example:
        >>> my_quiz_remarks_text = "See Rules 1.10.2 and 1.11"
        >>> my_rules_page_url = "https://zackjh.github.io/discquiz/"
        >>> result = format_quiz_remarks(my_quiz_remarks_text,
                                         my_rules_page_url)
        >>> print(result)
        "See Rules [1\.10\.2](https://zackjh\.github\.io/discquiz/\#1\.10\.2)
            and [1\.11](https://zackjh\.github\.io/discquiz/\#1\.11)"
    """

    # RegExp pattern to match valid rule numbers
    # A valid rule number is a string with integers separated by single periods
    # E.g 1.2, 1.2.3, 1.2.3.4
    rule_pattern = r"\d+(\.\d+)+"

    words = quiz_remarks_text.split()
    for i, word in enumerate(words):
        if word.lower() == "definition":
            url = escape_markdownv2(f"{rules_page_url}#Definitions")
            words[i] = f"[{word}]({url})"
        elif re.match(rule_pattern, word):
            if word[-1] == ".":
                word = word[0:-1]

            word_escaped = escape_markdownv2(word)
            url = escape_markdownv2(f"{rules_page_url}#{word}")

            words[i] = f"[{word_escaped}]({url})"
        else:
            continue

    return " ".join(words)
