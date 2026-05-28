from urllib.parse import parse_qs


def application(environ, start_response):
    method = environ.get('REQUEST_METHOD', 'GET')

    query_string = environ.get('QUERY_STRING', '')
    get_params = parse_qs(query_string)

    post_params = {}
    if method == 'POST':
        try:
            length = int(environ.get('CONTENT_LENGTH', 0) or 0)
        except ValueError:
            length = 0
        body = environ['wsgi.input'].read(length).decode('utf-8') if length > 0 else ''
        post_params = parse_qs(body)

    lines = []
    lines.append('GET parameters:')
    if get_params:
        for name, values in get_params.items():
            for value in values:
                lines.append('  ' + name + ' = ' + value)
    else:
        lines.append('  (empty)')

    lines.append('')
    lines.append('POST parameters:')
    if post_params:
        for name, values in post_params.items():
            for value in values:
                lines.append('  ' + name + ' = ' + value)
    else:
        lines.append('  (empty)')

    body = ('\n'.join(lines) + '\n').encode('utf-8')

    start_response('200 OK', [
        ('Content-Type', 'text/plain; charset=utf-8'),
        ('Content-Length', str(len(body))),
    ])
    return [body]
