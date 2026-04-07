# 2026-VK-EDU-Web-13-Izmaylov-M

## ДЗ 1

Реализованы HTML-страницы с использованием Bootstrap (без CDN):

- index.html — главная страница
- base.html — базовый шаблон (header, footer, head, общие блоки)
- ask.html — форма создания вопроса
- question.html — страница вопроса и ответов
- login.html — форма входа
- signup.html — форма регистрации
- settings.html — настройки профиля

Также добавлены стили в style.css.

---

## ДЗ 2

Проект переведён на Django:

- base.html используется как шаблон (extends)
- выделены общие компоненты через include
- реализованы views-заглушки (без базы данных)
- добавлены маршруты URL для всех страниц
- реализована пагинация (вынесена в отдельную функцию)
- настроена структура приложений core и questions

---

## Маршруты и функциональность

- список новых вопросов (главная страница)  
  URL: `/`  
  или нажатие на название сайта

- список “лучших” вопросов  
  URL: `/hot/`  
  или кнопка “Горячие вопросы”

- список вопросов по тэгу  
  URL: `/tag/<tag>/`  
  или нажатие на тэг в правой части экрана (на ПК) / внизу (на телефоне)

- страница одного вопроса со списком ответов  
  URL: `/question/<id>/`  
  или нажатие на карточку вопроса

- форма логина  
  URL: `/login/`  
  или нажатие на кнопку “Вход”

- форма регистрации  
  URL: `/signup/`  
  или нажатие на кнопку “Регистрация”

- форма редактирования профиля  
  URL: `/profile/`  
  (кнопка пока не добавлена, так как нет авторизации)

- форма создания вопроса  
  URL: `/ask/`  
  или нажатие на кнопку “Спросить”

---

## Окружение

### requirements.txt

Создан через:

pip freeze > requirements.txt

---

### .gitignore

Исключает:

- venv / .venv
- __pycache__ / *.pyc
- db.sqlite3
- .env
- media / staticfiles
- .idea / .vscode

---

### .env

Секретные данные вынесены в .env

Пример (.env.example):

SECRET_KEY=wandfbeufwundubwe67676767676767676767676767

DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1

---

### Docker

Добавлены:

- Dockerfile
- docker-compose.yml

---

## Запуск проекта

### Локально

```
python -m venv venv
pip install -r requirements.txt
python manage.py runserver
```

---

### Docker

```
docker compose up --build
```

После запуска:

http://localhost:8000
