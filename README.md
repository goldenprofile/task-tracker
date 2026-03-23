# Task Tracker

Desktop-приложение для управления задачами и проектами с канбан-доской.

## Возможности

- Канбан-доска с колонками **To Do / In Progress / Done**
- Проекты для группировки задач
- Приоритеты задач (Low / Medium / High)
- Локальная SQLite база данных
- Тёмная тема

## Технологии

- **Python 3.12+**
- **NiceGUI** — веб-интерфейс
- **SQLAlchemy 2** — ORM и работа с базой данных

## Установка

```bash
# Клонировать репозиторий
git clone https://github.com/your-username/task-tracker.git
cd task-tracker

# Установить зависимости (через uv)
uv sync
```

## Запуск

```bash
python run.py
```

Приложение откроется в браузере на [http://localhost:8080](http://localhost:8080).

## Структура проекта

```
task_tracker/
├── app.py          # Главная страница
├── models.py       # SQLAlchemy-модели (Project, Task)
├── database.py     # Подключение к БД
├── state.py        # Состояние приложения
├── theme.py        # Настройки темы
└── components/
    ├── kanban.py   # Канбан-доска
    ├── sidebar.py  # Боковая панель
    └── dialogs.py  # Диалоговые окна
```

## Лицензия

[MIT](LICENSE)
