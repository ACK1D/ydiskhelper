<h1 align="center">
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset=".github/YDiskHelper.svg">
        <img width="690" src=".github/YDiskHelper.svg" alt="YDiskHelper">
    </picture>
</h1>

> ⚠️ This is a test assignment, not intended for production use.

A web application for viewing and downloading files from Yandex.Disk public links.

[Русская версия](README.ru.md)

## Features
- View files from Yandex.Disk public links
- Download single or multiple files
- Filter files by type
- OAuth authorization support

## Requirements
- Python 3.12
- Poetry (not required, you can use `pip install -r requirements-dev.txt`)

## Installation

1. Clone the repository
2. Install Poetry:
```
pip install poetry
```
3. Install dependencies:
```
poetry install
```

## Installation via Docker

1. Clone the repository
2. Create `.env` file with the following parameters
3. Run the application:
```
task run_docker
```
or
```
docker compose up --build -d
```

## OAuth Setup

1. Register your application at [Yandex OAuth](https://oauth.yandex.ru/)
2. Get Client ID and Client Secret
3. Create `.env` file with the following parameters:
```bash
YANDEX_CLIENT_ID=your_client_id
YANDEX_CLIENT_SECRET=your_client_secret
YANDEX_OAUTH_TOKEN=your_oauth_token
YANDEX_REDIRECT_URI=http://localhost:8000/oauth/callback/
```
## Run the Application

1. Apply migrations:
```bash
poetry run python manage.py migrate
```
2. Start the development server:
```bash
poetry run python manage.py runserver
```

## Usage

1. Open http://localhost:8000 in your browser
2. Enter a Yandex.Disk public link
3. Select files to download
4. Click "Скачать выбранные файлы" for download

## Development

- Code style: Ruff
- Template formatting: djLint
- Python version: 3.12+

## Task Runner (optional)

Project includes Taskfile.yaml for common development tasks. If you have [Task](https://taskfile.dev) installed, run `task --list` to see available commands.