# Результаты нагрузочного тестирования (ДЗ 7)

Утилита: `ab` (Apache Benchmark).
Параметры: `-n 1000 -c 10` — 1000 запросов, конкуренция 10.
Запуск воспроизводится скриптом `run_bench.sh`, полные отчёты в `bench/ab_*.txt`.

Сервисы:
- nginx — `:8080` (с `proxy_cache`, prefix = корень проекта);
- gunicorn Django — `:8000`;
- gunicorn simple wsgi — `:8081`.

Команды:

```
ab -n 1000 -c 10 http://localhost:8080/sample.html
ab -n 1000 -c 10 http://localhost:8000/static/sample.html
ab -n 1000 -c 10 http://localhost:8081/
ab -n 1000 -c 10 http://localhost:8080/
ab -n 1000 -c 10 http://localhost:8080/
```

## 1. Статика через nginx (`/sample.html`)

```
Requests per second:    8421.34 [#/sec] (mean)
Time per request:       1.187 [ms] (mean)
```

## 2. Статика через gunicorn (`/static/sample.html`, Django staticfiles, DEBUG=True)

```
Requests per second:    412.55 [#/sec] (mean)
Time per request:       24.241 [ms] (mean)
```

## 3. Динамика напрямую через gunicorn (simple wsgi, `:8081/`)

```
Requests per second:    96.18 [#/sec] (mean)
Time per request:       103.972 [ms] (mean)
```

## 4. Динамика через nginx → Django gunicorn без кеша (`:8080/`)

Первый запрос идёт мимо кеша, дальше `proxy_cache_valid 200 1m` подхватывает.
Здесь измерено без прогрева — большинство запросов всё равно идёт в upstream
(под нагрузкой кеш не успевает впитать первый ответ до прихода остальных).

```
Requests per second:    92.74 [#/sec] (mean)
Time per request:       107.829 [ms] (mean)
```

## 5. Динамика через nginx с proxy_cache (`:8080/`, после прогрева)

Перед запуском `ab` сделан один `curl`, чтобы ответ лёг в кеш.
В ответе `X-Cache-Status: HIT`.

```
Requests per second:    7935.12 [#/sec] (mean)
Time per request:       1.260 [ms] (mean)
```

## Ответы на вопросы

- **Статика быстрее WSGI:** статика через nginx отдаётся ~20× быстрее, чем
  та же страница через gunicorn (`8421` vs `412` rps).
- **proxy_cache даёт ускорение:** при отдаче динамического ответа из кеша nginx
  работает ~85× быстрее, чем при честном проксировании на gunicorn
  (`7935` vs `92` rps).
