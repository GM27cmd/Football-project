from datetime import datetime

LOG_FILE = "commands.log"


def log_command(user_input, intent, response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_line = f"{timestamp} | {user_input} | {intent} | {response}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(log_line)
