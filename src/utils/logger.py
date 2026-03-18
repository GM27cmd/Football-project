import datetime

LOG_FILE = "commands.log"

def log_command(user_input, intent, params=None, result=None):
    """
    params: dict със съкратени параметри, напр. {"player": "Иван Петров", "from": "Левски", "to": "Лудогорец"}
    result: съобщение за успех или грешка
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    params_str = f" | PARAMS: {params}" if params else ""
    result_str = f" | RESULT: {result}" if result else ""
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | INPUT: {user_input} | INTENT: {intent}{params_str}{result_str}\n")
