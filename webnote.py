import socket
import re
import json
import urlparse

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(('0.0.0.0', 8080))
s.listen(1)
while True:
    data = ''
    conn, addr = s.accept()
    print 'Connected by', addr
    while True:
        if '\r\n\r\n' in data:
            break
        new_data = conn.recv(1024)
        if not new_data:
            break
        data += new_data

    request_match = \
            re.match(r'^([^ ]+) ([^ ]+) ([^ ]+)\r\n(.*)$', data, re.DOTALL)
    if request_match is not None:
        method = request_match.group(1)
        resource = request_match.group(2)
        protocol = request_match.group(3)
        data = request_match.group(4)
        request_match = \
                re.match(r'^([^ ]+) ([^ ]+) ([^ ]+)\r\n(.*)$', data , re.DOTALL)
    else:
        raise Exception('Cannot read request')

    request_headers = dict()

    while True:
        if data[:2] == '\r\n':
            data = data[2:]
            break
        field = re.match(r'^([^:]+): ([^\r]+)\r\n(.*)$', data, re.DOTALL)
        if field is not None:
            field_name = field.group(1)
            field_body = field.group(2)
            request_headers[field_name.lower()] = field_body
            data = field.group(3)
        else:
            raise Exception('Cannot read request header')

    response = ''

    response += 'HTTP/1.1 200 OK\r\n'

    try:
        with open('.notes') as note_file:
            note_dict = json.loads(note_file.read())
    except IOError:
        note_dict = dict()

    if resource == '/notes':
        response += 'Content-Type: text/plain; charset=utf-8\r\n'
        response += '\r\n'
        for name in note_dict:
            response += '%s\n' % name
    elif resource == '/add_note':
        response += 'Content-Type: text/html; charset=utf-8\r\n'
        response += '\r\n'
        if method == 'GET':
            response += """
            <html>
                <head>
                    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
                </head>
                <body>
                <form action="add_note" method="POST">
                    Name: <input type="text" name="name"/>
                    <br/>
                    Content: <input type="text" name="content"/>
                    <br/>
                    <input type="submit" value="Add"/>
                </form>
                </body>
            </html>
            """
        elif method == 'POST':
            while True:
                if len(data) != int (request_headers['content-length']):
                    data += conn.recv(1024)
                else:
                    break
            new_dict = urlparse.parse_qs(data)
            note_dict[new_dict['name'][0]] = new_dict['content'][0]
            with open('.notes', 'w') as note_file:
                json.dump(note_dict, note_file)

    else:
        try:
            note_match = re.match('^/notes/([a-z]+)$', resource)
            if note_match is not None:
                aux = note_dict[note_match.group(1)]
                response += 'Content-Type: text/plain; charset=utf-8\r\n'
                response += '\r\n'
                response += aux
            else:
                response += 'Hello World!!!'
        except KeyError:
            response += 'Content-Type: text/html; charset=utf-8\r\n'
            response += '\r\n'
            response += """
            <html>
                <head>
                    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
                </head>
                <body>
                    <h1>ERROR 404<h1>
                </body>
            </html>
            """

    conn.sendall(response)

    conn.close()
