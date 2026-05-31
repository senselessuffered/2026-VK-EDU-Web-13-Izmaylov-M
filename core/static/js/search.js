(function () {
    const widget = document.getElementById('search-widget');
    if (!widget) {
        return;
    }

    const input = document.getElementById('search-input');
    const dropdown = document.getElementById('search-suggestions');
    const url = widget.dataset.searchUrl;
    const DEBOUNCE_MS = 300;
    const MIN_LENGTH = 2;

    let timer = null;
    let controller = null;

    function escapeHtml(value) {
        const div = document.createElement('div');
        div.textContent = value == null ? '' : value;
        return div.innerHTML;
    }

    function hide() {
        dropdown.classList.add('d-none');
        dropdown.innerHTML = '';
    }

    function render(results) {
        if (!results.length) {
            dropdown.innerHTML =
                '<span class="list-group-item bg-dark text-white-50 border-secondary">Ничего не найдено</span>';
            dropdown.classList.remove('d-none');
            return;
        }
        dropdown.innerHTML = results.map(function (item) {
            return '<a href="' + item.url + '" ' +
                'class="list-group-item list-group-item-action bg-dark text-white border-secondary">' +
                '<span class="d-block text-truncate">' + escapeHtml(item.title) + '</span>' +
                '<small class="text-white-50">' + item.answers_count + ' ответов</small>' +
                '</a>';
        }).join('');
        dropdown.classList.remove('d-none');
    }

    function fetchSuggestions(query) {
        if (controller) {
            controller.abort();
        }
        controller = new AbortController();
        fetch(url + '?q=' + encodeURIComponent(query), {signal: controller.signal})
            .then(function (response) { return response.json(); })
            .then(function (data) { render(data.results || []); })
            .catch(function (error) { if (error.name !== 'AbortError') { hide(); } });
    }

    input.addEventListener('input', function () {
        const query = input.value.trim();
        if (timer) {
            clearTimeout(timer);
        }
        if (query.length < MIN_LENGTH) {
            hide();
            return;
        }
        timer = setTimeout(function () { fetchSuggestions(query); }, DEBOUNCE_MS);
    });

    input.addEventListener('focus', function () {
        if (dropdown.innerHTML) {
            dropdown.classList.remove('d-none');
        }
    });

    document.addEventListener('click', function (event) {
        if (!widget.contains(event.target)) {
            hide();
        }
    });
})();
