<h1 align="center">
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset=".github/YDiskHelper.svg">
        <img width="690" src=".github/YDiskHelper.svg" alt="YDiskHelper">
    </picture>
</h1>

> ⚠️ Это тестовое задание, не предназначенное для использования в продакшене.

Веб-приложение для просмотра и загрузки файлов с публичных ссылок Яндекс.Диска.

[English version](README.md)

## Возможности
- Просмотр файлов по публичной ссылке Яндекс.Диска
- Загрузка одного или нескольких файлов
- Фильтрация файлов по типу
- Поддержка OAuth авторизации

## Требования
- Python 3.12
- Poetry (не обязательно, можно использовать `pip install -r requirements-dev.txt`)

## Установка

1. Клонируйте репозиторий
2. Установите Poetry:
```
pip install poetry
```
3. Установите зависимости:
```
poetry install
```

## OAuth Setup

1. Зарегистрируйте приложение в [Yandex OAuth](https://oauth.yandex.ru/)
2. Получите Client ID и Client Secret
3. Создайте файл `.env` с параметрами:
```
YANDEX_CLIENT_ID=your_client_id
YANDEX_CLIENT_SECRET=your_client_secret
YANDEX_OAUTH_TOKEN=your_oauth_token
YANDEX_REDIRECT_URI=http://localhost:8000/oauth/callback/
```

## Запуск приложения

1. Примените миграции:
```
poetry run python manage.py migrate
```
2. Запустите сервер разработки:
```
poetry run python manage.py runserver
```

## Запуск через Docker

1. Убедитесь, что Docker установлен
2. Создайте файл `.env` с необходимыми параметрами
3. Запустите приложение:
```
task run_docker
```
или
```
docker compose up --build -d
```

## Использование

1. Откройте http://localhost:8000 в вашем браузере
2. Введите публичную ссылку Яндекс.Диска
3. Выберите файлы для загрузки
4. Нажмите "Скачать выбранные файлы" для загрузки

## Разработка

- Стиль кода: Ruff
- Форматирование шаблонов: djLint
- Версия Python: 3.12+

## Task Runner (опционально)

Проект включает Taskfile.yaml для выполнения частых задач разработки. Если у вас установлен [Task](https://taskfile.dev), выполните `task --list` для просмотра доступных команд.


