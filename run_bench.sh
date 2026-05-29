#!/usr/bin/env bash
set -euo pipefail

N=1000
C=10
OUT=bench
mkdir -p "$OUT"

NGINX=http://localhost:8080
GUNI_DJANGO=http://localhost:8000
GUNI_SIMPLE=http://localhost:8081

run() {
    local name=$1
    local url=$2
    echo "==> [$name] ab -n $N -c $C $url"
    ab -n "$N" -c "$C" "$url" > "$OUT/ab_${name}.txt" 2>&1 || {
        echo "    ab упал, см. $OUT/ab_${name}.txt"
        return 1
    }
    grep -E "Requests per second|Time per request|Document Length" "$OUT/ab_${name}.txt"
    echo
}

warmup_cache() {
    curl -s -o /dev/null "$NGINX/" || true
}

echo "1) Статика через nginx"
run static_nginx       "$NGINX/sample.html"

echo "2) Статика через gunicorn (Django staticfiles, DEBUG=True)"
run static_gunicorn    "$GUNI_DJANGO/static/sample.html"

echo "3) Динамика напрямую через gunicorn (simple wsgi)"
run dynamic_gunicorn   "$GUNI_SIMPLE/"

echo "4) Динамика через nginx -> Django gunicorn (без кеша)"
run dynamic_nginx      "$NGINX/nocache/"

echo "5) Динамика через nginx с proxy_cache (после прогрева)"
warmup_cache
run dynamic_nginx_cache "$NGINX/"

echo
echo "Готово. Подробные отчёты ab - в каталоге $OUT/."
echo "Сводку можно собрать так:"
echo "  grep 'Requests per second' $OUT/ab_*.txt"
