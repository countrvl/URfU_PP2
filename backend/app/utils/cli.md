# AI-Агент для деплоя проекта

## Назначение

Этот агент предназначен для автоматизации анализа, тестирования, деплоя и мониторинга проекта системы распознавания автомобильных номеров.

---

## Возможности

- Анализирует README.md и структуру проекта с помощью LLM Ollama (модель mistral)
- Запускает деплой через docker-compose
- Мониторит состояние контейнеров и рестартует упавшие (self-healing)
- Ведёт логирование действий и формирует отчёты
- CLI-интерфейс для управления

---

## Как запустить

1. Убедитесь, что Ollama установлен и в системе доступна модель `mistral`.  
   Проверить модели можно командой:
   ```bash
   ollama list
