import os
import subprocess
import json
import time
import requests

# Корень проекта - два уровня выше utils
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
OLLAMA_API_URL = "http://ollama:11434"
LOG_FILE = os.path.join(PROJECT_ROOT, "agent_logs.json")

def log_event(event_type, message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = {"timestamp": timestamp, "type": event_type, "message": message}
    print(f"[{timestamp}] [{event_type}] {message}")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(entry)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

def analyze_project():
    readme_path = os.path.join(PROJECT_ROOT, "README.md")
    if not os.path.isfile(readme_path):
        log_event("ERROR", "README.md не найден")
        return

    with open(readme_path, "r", encoding="utf-8") as f:
        readme_text = f.read()

    structure = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        rel_root = os.path.relpath(root, PROJECT_ROOT)
        structure.append({"path": rel_root, "dirs": dirs, "files": files})

    prompt = (
        "Проект описан следующим образом:\n"
        f"{readme_text}\n\n"
        "Структура каталогов и файлов:\n"
        f"{json.dumps(structure, indent=2, ensure_ascii=False)}\n\n"
        "Проанализируй проект, укажи ключевые моменты для успешного деплоя и потенциальные проблемы."
    )

    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/chat",
            json={"model": "llama2", "prompt": prompt},
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        analysis = result.get("response", "Нет ответа от LLM")
        log_event("ANALYSIS", analysis)
        print("\n--- Анализ проекта ---")
        print(analysis)
    except Exception as e:
        log_event("ERROR", f"Ошибка при запросе к LLM: {e}")

def run_docker_compose():
    try:
        cmd = ["docker-compose", "-f", os.path.join(PROJECT_ROOT, "docker-compose.yml"), "up", "-d", "--build"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        log_event("DEPLOY_STDOUT", proc.stdout)
        log_event("DEPLOY_STDERR", proc.stderr)
        if proc.returncode == 0:
            log_event("DEPLOY", "Деплой выполнен успешно")
            print("Деплой выполнен успешно")
        else:
            log_event("ERROR", f"Деплой завершился с ошибкой (код {proc.returncode})")
            print(f"Ошибка деплоя, код: {proc.returncode}")
    except Exception as e:
        log_event("ERROR", f"Ошибка при деплое: {e}")

def check_containers():
    try:
        cmd = ["docker", "ps", "-a", "--format", "{{.ID}} {{.Names}} {{.Status}}"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if proc.returncode != 0:
            log_event("ERROR", f"Ошибка проверки контейнеров: {proc.stderr}")
            print("Ошибка при проверке контейнеров")
            return

        print("\n--- Статус контейнеров ---")
        containers = []
        for line in proc.stdout.strip().split("\n"):
            cid, name, status = line.split(maxsplit=2)
            containers.append({"id": cid, "name": name, "status": status})
            print(f"{name}: {status}")
        log_event("MONITOR", json.dumps(containers, ensure_ascii=False))

        for c in containers:
            if "Exited" in c["status"] or "Restarting" in c["status"]:
                print(f"Рестарт контейнера {c['name']}")
                subprocess.run(["docker", "restart", c["id"]])
                log_event("SELF_HEALING", f"Рестарт контейнера {c['name']}")

    except Exception as e:
        log_event("ERROR", f"Ошибка мониторинга: {e}")

def show_report():
    if not os.path.isfile(LOG_FILE):
        print("Логи отсутствуют")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = json.load(f)

    print("\n--- Отчёт агента ---")
    for entry in logs[-20:]:
        print(f"[{entry['timestamp']}] [{entry['type']}] {entry['message']}")

def main():
    print("=== AI-Агент по заданию ===")
    while True:
        print(
            "\nДоступные команды:\n"
            "1. analyze - Анализировать проект\n"
            "2. deploy  - Запустить деплой\n"
            "3. monitor - Проверить контейнеры и self-healing\n"
            "4. report  - Показать отчёт\n"
            "5. exit    - Выход\n"
        )
        cmd = input("Введите команду: ").strip().lower()
        if cmd == "analyze":
            analyze_project()
        elif cmd == "deploy":
            run_docker_compose()
        elif cmd == "monitor":
            check_containers()
        elif cmd == "report":
            show_report()
        elif cmd == "exit":
            print("Выход...")
            break
        else:
            print("Неизвестная команда")

if __name__ == "__main__":
    main()
