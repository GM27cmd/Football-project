import json
import os


INTENTS_FILE = os.path.join(os.path.dirname(__file__), "intents.json")


def load_intents():
    with open(INTENTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def detect_intent(user_input):
    user_input = user_input.lower()
    intents = load_intents()

    for intent, data in intents.items():
        for pattern in data["patterns"]:
            if pattern in user_input:
                return intent

    return "unknown"
