# DiscQuiz

DiscQuiz is a Telegram bot that sends periodic quiz questions based on the [WFDF Advanced Accreditation Quiz](https://rules.wfdf.sport/accreditation/advanced/).

## Installation

DiscQuiz has been developed using Docker Compose, hence it is recommended that you use Docker Compose to run the bot.

1. Install [Docker Desktop](https://docs.docker.com/get-docker/) (or [Docker Engine](https://docs.docker.com/engine/install/) if you are using a Linux machine).

2. Copy `docker-compose.yml` into your local machine.

3. In your `docker-compose.yml`, update the `DAILY_LEADERBOARD_TIME`, `LIST_OF_ADMINS`, `LOCAL_TIMEZONE`, and `TELEGRAM_BOT_API_TOKEN` environment variables with the appropriate values.

   - Obtain your Telegram user ID using [this guide](https://www.itgeared.com/how-to-find-someones-telegram-id/#How%20To%20Find%20Someone's%20Telegram%20Id:~:text=you%20find%20it.-,How%20To%20Find%20Someone%E2%80%99s%20Telegram%20ID,-Your%20Telegram%20ID).
   - Find your local timezone from [this list](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568).
   - Create a new Telegram Bot and obtain your bot token using [this guide](https://core.telegram.org/bots/tutorial#obtain-your-bot-token).

   Your `docker-compose.yml` should look similar to this:

   ```yml
   services:
     server:
       image: discquiz-server
       container_name: discquiz-server
       volumes:
         - discquiz-db:/etc/discquiz
       environment:
         DATABASE_PATH: /etc/discquiz/discquiz.db
     telegram-bot:
       image: discquiz-telegram-bot
       container_name: discquiz-telegram-bot
       environment:
         DAILY_LEADERBOARD_TIME: 12:00
         FLASK_API_URL: http://discquiz-server:5000
         LIST_OF_ADMINS: "[123456789]"
         LOCAL_TIMEZONE: Asia/Singapore
         RULES_PAGE_URL: https://zackjh.github.io/discquiz/
         TELEGRAM_BOT_API_TOKEN: 4839574812:AAFD39kkdpWt3ywyRZergyOLMaJhac60qc

   volumes:
     discquiz-db:
   ```

4. Start the application using:

   ```
   $ docker compose up
   ```

## Adding quiz questions to the database

The database does not have any quiz questions when the application is first initialised. Follow these steps to add quiz questions to the database:

1. Take the [WFDF Advanced Accreditation Quiz](https://rules.wfdf.sport/accreditation/advanced/).

2. Save the result page as a HTML file using [this guide](https://www.wikihow.com/Save-a-Webpage).

3. Copy the HTML file from your local machine into the `discquiz-server` container using:

   ```
   $ docker cp <local path to HTML file> discquiz-server:/app
   ```

4. Run `config.py` in the `discquiz-server` container using:

   ```
   $ docker exec -it discquiz-server python config.py
   ```

5. Follow the instructions in the CLI to add quiz questions to the database.

   When prompted for the file path of the HTML file, enter the name of your HTML file (e.g. my_webpage.html).

6. Optionally, once you have added the quiz questions to the database, remove the HTML file from the `discquiz-server` container using:
   ```
   $ docker exec discquiz-server rm <name of HTML file>
   ```

## Usage

### Telegram Bot Commands

| Command          | Arguments            | Functionality                                              | Usage Example   |
| ---------------- | -------------------- | ---------------------------------------------------------- | --------------- |
| `/start`         | None                 | Checks if the bot is running properly.                     | `/start`        |
| `/new <time>`    | Time in HH:MM format | Sets up a quiz to be sent at the specified {time} daily.   | `/new 10:35`    |
| `/remove <time>` | Time in HH:MM format | Removes the daily quiz scheduled for the specified {time}. | `/remove 10:35` |
| `/schedule`      | None                 | Displays all currently scheduled daily quizzes.            | `/schedule`     |

## Future Enhancements

- [ ] Add the ability to schedule a daily leaderboard message
- [ ] Improve design of [rules webpage](https://zackjh.github.io/discquiz/)
