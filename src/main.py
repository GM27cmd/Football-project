from chatbot.nlu import detect_intent
from chatbot.router import route_intent
from utils.logger import log_command
from chatbot.help import show_help

def main():
    print("⚽ FootballAI Assistant")
    print("Напиши 'помощ' за всички команди.\n")

    while True:
        user_input = input("> ").strip()

        if not user_input:
            continue

        # директна помощ (без NLU)
        if user_input.lower() in ["помощ", "help"]:
            print(show_help())
            continue

        if user_input.lower() in ["изход", "exit", "quit"]:
            print("👋 Изход от програмата.")
            break

        intent = detect_intent(user_input)
        response = route_intent(intent, user_input)

        print(response)

        log_command(user_input, intent, response)


if __name__ == "__main__":
    main()
