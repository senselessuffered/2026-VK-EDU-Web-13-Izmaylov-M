(function () {
    const cfg = document.getElementById('realtime-config');
    if (!cfg || typeof Centrifuge === 'undefined') {
        return;
    }

    const wsUrl = cfg.dataset.wsUrl;
    const token = cfg.dataset.token;
    const channel = cfg.dataset.channel;
    const currentUserId = parseInt(cfg.dataset.userId, 10) || 0;
    const isFirstPage = cfg.dataset.firstPage === 'true';
    const list = document.getElementById('answers-list');

    function escapeHtml(value) {
        const div = document.createElement('div');
        div.textContent = value == null ? '' : value;
        return div.innerHTML;
    }

    function buildAnswerCard(data) {
        const wrapper = document.createElement('div');
        wrapper.className = 'answer-item mb-3';
        wrapper.id = 'answer-' + data.answer_id;
        wrapper.innerHTML =
            '<div class="card-body p-4">' +
                '<div class="d-flex gap-3">' +
                    '<div class="text-center">' +
                        '<div class="fw-bold my-2 text-white">' + (data.rating || 0) + '</div>' +
                    '</div>' +
                    '<img src="' + data.avatar_url + '" class="rounded-circle" width="40" height="40" alt="avatar">' +
                    '<div class="flex-grow-1">' +
                        '<p class="text-white-50 mb-2">Ответил ' + escapeHtml(data.created_at) +
                            ' <strong class="text-white">' + escapeHtml(data.author_username) + '</strong></p>' +
                        '<p class="mb-0 text-white">' + escapeHtml(data.text) + '</p>' +
                    '</div>' +
                '</div>' +
            '</div>';
        return wrapper;
    }

    function handlePublication(data) {
        if (!data || !data.answer_id) {
            return;
        }
        if (currentUserId && data.author_id === currentUserId) {
            return;
        }
        if (document.getElementById('answer-' + data.answer_id)) {
            return;
        }

        if (isFirstPage && list) {
            const placeholder = document.getElementById('no-answers');
            if (placeholder) {
                placeholder.remove();
            }
            list.appendChild(buildAnswerCard(data));
        } else {
            alert('Появился новый ответ на этот вопрос. Обновите страницу, чтобы увидеть его.');
        }
    }

    const centrifuge = new Centrifuge(wsUrl, {token: token});
    const subscription = centrifuge.newSubscription(channel);
    subscription.on('publication', function (ctx) { handlePublication(ctx.data); });
    subscription.subscribe();
    centrifuge.connect();
})();
