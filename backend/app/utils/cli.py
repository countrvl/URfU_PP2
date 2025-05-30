import sys
import logging
import subprocess
import json
import time

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)

LOG_PATH = "agent_logs.json"

def log_event(event_type, message):
    entry = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "type": event_type, "message": message}
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logging.error(f"Ошибка записи лога: {e}")

def ask_llm(prompt: str) -> str | None:
    try:
        process = subprocess.run(
            ["ollama", "run", "mistral"],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
        if process.returncode != 0:
            err = process.stderr.decode("utf-8").strip()
            logging.error(f"Ollama error: {err}")
            log_event("ERROR", f"Ollama error: {err}")
            return None
        output = process.stdout.decode("utf-8").strip()
        return output
    except Exception as e:
        logging.error(f"Ошибка при вызове ollama: {e}")
        log_event("ERROR", f"Ошибка при вызове ollama: {e}")
        return None

def analyze_project():
    logging.info("Запрос к LLM для анализа проекта...")
    prompt = (
        "Проанализируй проект в текущей директории (структура, основные файлы и функции). "
        "Дай краткий отчёт, упомяни README.md, docker-compose.yml и backend."
    )
    response = ask_llm(prompt)
    if response:
        logging.info(f"Ответ LLM:\n{response}")
        log_event("ANALYZE", response)
    else:
        logging.error("Не удалось получить ответ от LLM")
        log_event("ERROR", "Не удалось получить ответ от LLM")

def deploy_project():
    logging.info("Запуск деплоя через docker compose up --build -d...")
    try:
        result = subprocess.run(
            ["docker", "compose", "up", "--build", "-d"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300,
        )
        logging.info(f"DEPLOY STDOUT:\n{result.stdout}")
        if result.stderr:
            logging.error(f"DEPLOY STDERR:\n{result.stderr}")
        log_event("DEPLOY_STDOUT", result.stdout)
        if result.stderr:
            log_event("DEPLOY_STDERR", result.stderr)
        if result.returncode == 0:
            logging.info("Деплой завершён успешно.")
            log_event("DEPLOY", "Деплой завершён успешно.")
        else:
            logging.error(f"Деплой завершился с ошибкой, код {result.returncode}")
            log_event("ERROR", f"Деплой завершился с ошибкой, код {result.returncode}")
    except Exception as e:
        logging.error(f"Ошибка при деплое: {e}")
        log_event("ERROR", f"Ошибка при деплое: {e}")

def monitor_containers():
    logging.info("Проверка статуса docker-контейнеров...")
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{json .}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            logging.error(f"Ошибка docker ps: {result.stderr}")
            log_event("ERROR", f"Ошибка docker ps: {result.stderr}")
            return

        containers = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
        status_summary = [
            {"id": c.get("ID"), "name": c.get("Names"), "status": c.get("Status")}
            for c in containers
        ]
        logging.info(f"Контейнеры:\n{status_summary}")
        log_event("MONITOR", json.dumps(status_summary, ensure_ascii=False))
    except Exception as e:
        logging.error(f"Ошибка при мониторинге контейнеров: {e}")
        log_event("ERROR", f"Ошибка при мониторинге контейнеров: {e}")

def show_report():
    logging.info("--- Отчёт агента ---")
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    print(f"[{entry['time']}] [{entry['type']}] {entry['message']}")
                except json.JSONDecodeError as e:
                    logging.error(f"Ошибка декодирования JSON в логе: {e} - Строка: {line}")
    except FileNotFoundError:
        logging.info("Отчёт пуст. Логов ещё нет.")
    except Exception as e:
        logging.error(f"Ошибка при чтении отчёта: {e}")


def main():
    logging.info("=== AI-Агент по заданию ===")

    while True:
        print(
            "\nДоступные команды:\n"
            "1. analyze - Анализировать проект\n"
            "2. deploy  - Запустить деплой\n"
            "3. monitor - Проверить контейнеры и self-healing\n"
            "4. report  - Показать отчёт\n"
            "5. exit    - Выход"
        )
        cmd = input("Введите команду: ").strip().lower()

        if cmd in ("1", "analyze"):
            analyze_project()
        elif cmd in ("2", "deploy"):
            deploy_project()
        elif cmd in ("3", "monitor"):
            monitor_containers()
        elif cmd in ("4", "report"):
            show_report()
        elif cmd in ("5", "exit"):
            logging.info("Выход...")
            sys.exit(0)
        else:
            logging.info("Неизвестная команда")

if __name__ == "__main__":
    main()
