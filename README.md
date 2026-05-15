# 2026-VK-EDU-Web-13-Izmaylov-M

## ДЗ 1

Реализованы HTML-страницы с использованием Bootstrap без CDN:

- `index.html` — главная страница со списком вопросов;
- `base.html` — базовый шаблон с header, footer и общими блоками;
- `ask.html` — форма создания вопроса;
- `question.html` — страница вопроса и ответов;
- `login.html` — форма входа;
- `signup.html` — форма регистрации;
- `settings.html` — настройки профиля.

Также добавлены общие стили в `style.css`.

---

## ДЗ 2

Проект переведен на Django:

- настроены приложения `core` и `questions`;
- подключены шаблоны через `{% extends %}` и `{% include %}`;
- добавлены маршруты для основных страниц;
- реализованы view-заглушки;
- добавлена пагинация списка вопросов;
- статика разложена по приложениям.

---

## ДЗ 3

Добавлена работа с базой данных:

- созданы модели `Profile`, `Question`, `Answer`, `Tag`, `QuestionLike`, `AnswerLike`;
- настроены связи между пользователями, вопросами, ответами, тегами и лайками;
- добавлены ограничения на повторные лайки через `unique_together`;
- добавлены managers для новых, лучших и теговых вопросов;
- настроена Django admin-панель;
- добавлены inline-профиль на странице пользователя и inline-ответы на странице вопроса;
- страницы вопросов переведены с заглушек на ORM;
- добавлены состояния пустоты;
- подключен `django-debug-toolbar` при `DEBUG=True`;
- настроен PostgreSQL через env-файлы;
- обновлен `docker-compose.yml` с сервисом БД и volume;
- добавлена команда наполнения базы:

```bash
python manage.py fill_db 10000
```

Команда создает:

- пользователей: `ratio`;
- вопросов: `ratio * 10`;
- ответов: `ratio * 100`;
- тегов: `ratio`;
- оценок: `ratio * 200`.

---

## ДЗ 4

Добавлена авторизация и обработка форм:

- `/login/` — вход по логину и паролю;
- `/login/?next=...` — редирект после успешного входа;
- внешний `next` валидируется и не используется для редиректа;
- `/signup/` — регистрация пользователя;
- при регистрации создается связанный `Profile`;
- пароль проверяется стандартными валидаторами Django;
- `/logout/` — выход с возвратом на текущую страницу;
- `/profile/` — редактирование `email`, `username`, `avatar`;
- `/ask/` — добавление вопроса через `ModelForm`;
- добавление ответа на странице вопроса через `ModelForm`;
- после добавления ответа есть редирект на страницу с якорем ответа;
- для гостей недоступные кнопки отключены и имеют подсказки.

Ошибки форм выводятся на странице и введенные данные сохраняются.

---

## Основные маршруты

- `/` — новые вопросы;
- `/hot/` — лучшие вопросы;
- `/tag/<tag>/` — вопросы по тегу;
- `/question/<id>/` — страница вопроса;
- `/ask/` — создание вопроса;
- `/login/` — вход;
- `/signup/` — регистрация;
- `/logout/` — выход;
- `/profile/` — профиль;
- `/admin/` — админка.

---

## Окружение

Секреты и настройки БД вынесены в env-файлы.

Используются два локальных файла:

- `.env.local` — для запуска Django с компьютера через `python manage.py runserver`;
- `.env.docker` — для запуска Django внутри `docker compose`.

В репозитории есть пример:

```text
.env.example
```

Локальные env-файлы не добавляются в git:

```text
.env.local
.env.docker
```

---

## !!!Запуск

Через Docker:

```bash
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Локально:

Если нужно запускать Django локально через `python manage.py runserver`, базу все равно нужно поднять отдельно:

```bash
docker compose up -d db
python manage.py migrate
python manage.py runserver
```

## !!!Генерация тестовых данных + запуск

Для наполнения базы используется management command:

```text
questions/management/commands/fill_db.py
```

Команда запускается так:

```bash
python manage.py fill_db 1000
```

Число в конце — это `ratio`, коэффициент заполнения базы.

Если проект запускается через Docker:

```bash
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py fill_db 1000
```

Если Django запускается локально, а PostgreSQL только в Docker:

```bash
docker compose up -d db
python manage.py migrate
python manage.py fill_db 1000
python manage.py runserver
```

После запуска сайт доступен по адресу:

```text
http://127.0.0.1:8000/
```
