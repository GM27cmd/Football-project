import datetime

LOG_FILE = "commands.log"


def log_command(user_input, intent, result):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} | INPUT: {user_input} | INTENT: {intent} | RESULT: {result}\n")
