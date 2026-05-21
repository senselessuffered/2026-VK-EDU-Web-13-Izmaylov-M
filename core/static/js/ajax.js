function getCsrfToken() {
    const cookies = document.cookie ? document.cookie.split(';') : [];
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith('csrftoken=')) {
            return cookie.substring('csrftoken='.length);
        }
    }
    return '';
}

function postAjax(url, data) {
    const formData = new FormData();
    for (const key in data) {
        formData.append(key, data[key]);
    }
    return fetch(url, {
        method: 'POST',
        headers: {'X-CSRFToken': getCsrfToken()},
        body: formData,
    }).then(async (response) => {
        let body = null;
        try {
            body = await response.json();
        } catch (e) {
            body = null;
        }
        return {ok: response.ok, status: response.status, body};
    });
}

function setupVoteButtons() {
    const buttons = document.querySelectorAll('.js-vote');
    buttons.forEach((btn) => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const group = btn.closest('.js-vote-group');
            if (!group) {
                return;
            }
            const url = group.dataset.voteUrl;
            const targetId = group.dataset.voteTarget;
            const value = parseInt(btn.dataset.value, 10);

            postAjax(url, {target_id: targetId, value: value}).then(({ok, status, body}) => {
                if (ok) {
                    const ratingEl = group.querySelector('.js-rating');
                    if (ratingEl) {
                        ratingEl.textContent = body.rating;
                    }
                    group.querySelectorAll('.js-vote').forEach((b) => b.classList.remove('active'));
                    const active = group.querySelector('.js-vote[data-value="' + body.user_value + '"]');
                    if (active) {
                        active.classList.add('active');
                    }
                    return;
                }
                if (status === 401) {
                    const loginUrl = group.dataset.loginUrl || '/login/';
                    window.location.href = loginUrl;
                } else if (status === 405) {
                    alert('Метод запроса не разрешён.');
                } else if (status === 400) {
                    alert('Неверные данные запроса.');
                } else if (status === 403) {
                    alert('Действие запрещено.');
                } else {
                    alert('Не удалось проголосовать.');
                }
            }).catch(() => {
                alert('Сетевая ошибка. Попробуйте ещё раз.');
            });
        });
    });
}

function setupCorrectButtons() {
    const buttons = document.querySelectorAll('.js-correct');
    buttons.forEach((btn) => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const url = btn.dataset.url;
            const answerId = btn.dataset.answerId;

            postAjax(url, {answer_id: answerId}).then(({ok, status, body}) => {
                if (ok) {
                    const answerBlock = document.getElementById('answer-' + answerId);
                    if (answerBlock) {
                        const badge = answerBlock.querySelector('.js-correct-badge');
                        if (badge) {
                            badge.classList.toggle('d-none', !body.is_correct);
                        }
                    }
                    btn.classList.toggle('active', body.is_correct);
                    btn.textContent = body.is_correct ? 'Снять отметку' : 'Отметить правильным';
                    return;
                }
                if (status === 401) {
                    window.location.href = btn.dataset.loginUrl || '/login/';
                } else if (status === 403) {
                    alert('Только автор вопроса может выбирать правильный ответ.');
                } else if (status === 405) {
                    alert('Метод запроса не разрешён.');
                } else if (status === 400) {
                    alert('Неверные данные запроса.');
                } else {
                    alert('Не удалось обновить ответ.');
                }
            }).catch(() => {
                alert('Сетевая ошибка. Попробуйте ещё раз.');
            });
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    setupVoteButtons();
    setupCorrectButtons();
});
