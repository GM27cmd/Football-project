from src.chatbot.nlu import detect_intent
from src.chatbot.router import route_intent
from src.utils.logger import log_command


def main():
    print("⚽ Football Database Chatbot")
    print("Напиши 'помощ' за списък с команди.")

    while True:
        user_input = input("\n> ")

        intent = detect_intent(user_input)
        response = route_intent(intent, user_input)

        if response == "exit":
            print("Изход от програмата.")
            break

        print(response)
        log_command(user_input, intent, response)


if __name__ == "__main__":
    main()
