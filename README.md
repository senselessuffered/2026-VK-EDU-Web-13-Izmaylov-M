# 2026-VK-EDU-Web-13-Izmaylov-M

AskPupkin — учебный аналог StackOverflow на Django.

---

## Запуск через Docker (из коробки)

```bash
docker compose up --build
```

Поднимется вся инфраструктура:
- `db` — PostgreSQL с БД `askme`;
- `redis` — брокер celery и cache backend django (разные db: cache=1, broker=2, beat=3);
- `web` — Django: дождётся БД (healthcheck), выполнит `migrate` и запустит `runserver` на `0.0.0.0:8000`;
- `celery` — worker для фоновых задач (email, centrifugo, пересчёт кешей);
- `celerybeat` — периодический запуск задач (расписание в Redis через redbeat);
- `centrifugo` — websocket-сервер (на хосте порт `8001`);
- `maildev` — SMTP для локальной разработки (веб-интерфейс на `1080`, SMTP на `1025`).

После старта:
- сайт — `http://127.0.0.1:8000/`;
- почтовый ящик maildev — `http://127.0.0.1:1080/`;
- Centrifugo — `ws://localhost:8001/connection/websocket`.

### Создать суперпользователя для админки

```bash
docker compose exec web python manage.py createsuperuser
```

Админка: `http://127.0.0.1:8000/admin/`.

### Наполнить базу тестовыми данными

```bash
docker compose exec web python manage.py fill_db 1000
```

Число — это `ratio`. На выходе будет: `ratio` пользователей, `ratio` тегов, `ratio * 10` вопросов, `ratio * 100` ответов, `ratio * 200` лайков.

---

## Локальный запуск (без Docker для Django)

PostgreSQL удобно держать в Docker, а сам Django запускать с хоста:

```bash
docker compose up -d db

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env.local      # один раз; в .env.local оставьте DB_HOST=localhost
python manage.py migrate
python manage.py runserver
```

---

## Переменные окружения

В репозитории лежит пример: `.env.example`. Реальные файлы в git не попадают:

- `.env.local` — для запуска `python manage.py runserver` с хоста;
- `.env.docker` — опциональный файл для переопределения переменных в контейнере. Не обязателен: значения по умолчанию заданы прямо в `docker-compose.yml`, поэтому проект поднимается без него.

---

## Структура проекта

```
application/   - настройки Django (settings.py, urls.py, celery.py)
core/          - пользователи: регистрация, вход, профиль, аватарки
questions/     - вопросы, ответы, теги, лайки, fill_db, celery-таски, поиск, centrifugo
centrifugo/    - конфиг сервера Centrifugo (config.json)
core/static/   - общая статика (css, js, картинки)
media/         - загруженные пользователями файлы (создаётся автоматически)
```

---

## Маршруты

Страницы:
- `/` — новые вопросы;
- `/hot/` — лучшие вопросы;
- `/tag/<tag>/` — вопросы по тегу;
- `/question/<id>/` — страница вопроса;
- `/ask/` — создание вопроса;
- `/login/`, `/signup/`, `/logout/`, `/profile/` — авторизация и профиль;
- `/admin/` — админка.

AJAX:
- `POST /ajax/vote-question/` — параметры `target_id`, `value` (`1` или `-1`);
- `POST /ajax/vote-answer/` — параметры `target_id`, `value` (`1` или `-1`);
- `POST /ajax/mark-correct/` — параметр `answer_id`;
- `GET  /search/?q=<текст>` — полнотекстовый поиск по вопросам, JSON-подсказки.

---

## Что сделано по домашним заданиям

### ДЗ 1 — вёрстка
Bootstrap без CDN, шаблоны `base.html`, `index.html`, `question.html`, `ask.html`, `login.html`, `signup.html`. Общие стили в `style.css`.

### ДЗ 2 — Django, view'хи и шаблоны
- приложения `core` и `questions`;
- наследование шаблонов через `extends` и `include` (`particles/card.html`, `particles/answer.html`, `particles/pagination.html`);
- именованные маршруты в `urls.py`, в шаблонах используются теги `url` и `static`;
- пагинация вынесена в функцию `paginate(request, objects, per_page=10)` (`questions/services.py`);
- `requirements.txt`, `.gitignore`, `Dockerfile`, `docker-compose.yml` в наличии.

### ДЗ 3 — модели, БД, наполнение
- модели `Profile`, `Question`, `Answer`, `Tag`, `QuestionLike`, `AnswerLike`;
- `unique_together` на лайках, чтобы один пользователь не накручивал;
- `QuestionManager` с методами `new()`, `best()`, `by_tag()`;
- админка с локализацией, `list_display`, `search_fields`, `list_filter`, `raw_id_fields`, инлайн профиля у пользователя и инлайн ответов у вопроса;
- команда наполнения базы `python manage.py fill_db <ratio>`. Логика разнесена по методам: `create_users`, `create_tags`, `create_questions`, `create_answers`, `create_likes`;
- `django-debug-toolbar` подключается только при `DEBUG=True`;
- PostgreSQL поднят как отдельный сервис в `docker-compose.yml` с `volume` и `healthcheck`;
- параметры подключения вынесены в `.env`, в репозитории — `.env.example`.

### ДЗ 4 — авторизация и формы
- `/login/` — вход, поддержка `?next=...` с валидацией через `url_has_allowed_host_and_scheme`;
- `/signup/` — регистрация, пароль проверяется через `AUTH_PASSWORD_VALIDATORS`, при успехе сразу создаётся `Profile`;
- `/logout/` — выход с возвратом на текущую страницу (через Referer);
- `/profile/` — `login_required`, редактирование `email`, `username`, `avatar`;
- `/ask/` — `ModelForm` для вопроса, теги тоже в форме;
- ответ на странице вопроса — отдельная `ModelForm`, после успеха редирект на страницу с правильной пагинацией и якорем `#answer-<id>`;
- для гостей кнопки «Спросить» и «Ответить» задизейблены и имеют подсказку.

Логика валидации лежит в `clean_*` методах форм, сохранение и связанные сущности — в `save()`. Во view только обработка GET/POST и редиректы.

### ДЗ 5 — аватарки и AJAX
- настроены `MEDIA_URL` и `MEDIA_ROOT`, медиа отдаётся при `DEBUG=True`;
- аватарка загружается через форму профиля, сохраняется в `MEDIA_ROOT/avatars/`, имя файла генерируется через `uuid4` (путь непредсказуем);
- на бэкенде валидируется расширение (`jpg, jpeg, png, gif, webp`) и размер (до 5 МБ);
- если аватарки нет — показывается дефолтная картинка из `static`;
- лайк/дизлайк вопроса и ответа — AJAX, возвращают новый рейтинг;
- отметка правильного ответа — AJAX, доступна только автору вопроса;
- ответы — `JsonResponse`, CSRF берётся из cookie;
- на клиенте обрабатываются ошибки 401 (редирект на логин), 403, 405, 400.

### ДЗ 6 — Redis, Celery, Centrifugo, email, поиск

**Redis + Celery + Celerybeat.** Redis — брокер celery (`CELERY_BROKER_URL`) и cache backend django (`django_redis`). Разные базы: cache=1, broker=2, beat=3. Расписание celerybeat хранится в Redis через `redbeat` (`CELERY_BEAT_SCHEDULER`). Все параметры подключения — в конфиге (`settings.py` читает их из `.env`). Приложение celery — `application/celery.py`, таски — `questions/tasks.py`. Сервисы `redis`, `celery`, `celerybeat` добавлены в `docker-compose.yml`.

**Кеширование через Celery.** Правая колонка (популярные теги за 3 месяца, лучшие участники за неделю) считается тяжёлыми запросами, поэтому кешируется. Две периодические таски `refresh_popular_tags` и `refresh_best_members` пересчитывают кеш по расписанию из `settings.py` (`CELERY_BEAT_SCHEDULE`, интервалы из `.env`). Данные показываются через inclusion-теги (`questions/templatetags/sidebar_tags.py`): берутся из кеша, а при промахе вьюха забирает их из БД и сразу прогревает кеш (`questions/services.py`).

**Real-time (Centrifugo).** Поднят сервер `centrifugo` (на хосте порт `8001`), один namespace `questions` с `allow_subscribe_for_client`. Connection-токены (JWT, HS256) генерируются на бэке (`questions/centrifugo.py`), секреты — в конфиге. При новом ответе вьюха ставит celery-таску `publish_new_answer`, которая шлёт сообщение в канал `questions:question_<id>` через HTTP API. На странице вопроса `centrifuge-js` слушает канал (`core/static/js/realtime.js`): первый ответ к вопросу без ответов и ответы на первой странице добавляются без перезагрузки, на остальных страницах показывается alert.

**Email.** Уведомление автору вопроса о новом ответе шлётся в celery-таске `send_new_answer_email` через `django.core.mail.send_mail`. Параметры SMTP — в конфиге. Для разработки поднят `maildev` (SMTP `1025`, веб-интерфейс `1080`).

**Полнотекстовый поиск.** Поиск по заголовку и тексту вопросов на полнотекстовом GIN-индексе PostgreSQL (`SearchVector('title', 'text', config='russian')`, миграция `0002`), а не `icontains`. Эндпоинт `GET /search/?q=` возвращает JSON-подсказки. В шапке — выпадающий список подсказок, запрос уходит по мере ввода с debounce и отменой предыдущего запроса (`core/static/js/search.js`).
