import re
import json
import os

# Зареждаме intents.json
intents_file = os.path.join(os.path.dirname(__file__), "intents.json")
with open(intents_file, encoding="utf-8") as f:
    intents_data = json.load(f)

def detect_intent(user_input):
    user_input = user_input.strip().lower()

    # Проверка спрямо intents.json regex
    for intent_item in intents_data:
        pattern = intent_item.get("regex", "")
        if pattern and re.search(pattern, user_input, re.IGNORECASE):
            return intent_item["tag"]

    # Ако няма съвпадение
    return "unknown"
