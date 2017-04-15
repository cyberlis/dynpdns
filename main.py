from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import base64
import sqlite3
import time
import os


DBFILENAME = '/var/lib/powerdns/pdns.sqlite3'
LOGIN = 'myuser'
PASSWORD = 'mypassword'
SERVERIP = ''
SERVERPORT = 10001
DOMAIN = 'cloud.rccraft.ru'
SOA_CONTENT = 'dyndns.ns.rccraft.ru admin.rccraft.ru {} 60 60 60 60'



class CustomServer(HTTPServer):
    def __init__(self, server_address, handler, login, password):
        super().__init__(server_address, handler)
        self.credentials = "%s:%s" % (login, password)
        self.login = login
        self.password = password
        self.auth = base64.b64encode(self.credentials.encode('utf-8')).decode()


class CustomHandler(BaseHTTPRequestHandler):
    ''' Main class to present webpages and authentication. '''

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type',
                         'text/plain; charset=utf-8')
        self.end_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="DyndnsCustomServer"')
        self.end_headers()

    def check_authentication(self):
        auth = self.headers.get('Authorization')
        if auth != "Basic %s" % self.server.auth:
            self.do_AUTHHEAD()
            return False
        return True

    def update_dns(self):
        now = int(time.time())
        with sqlite3.connect(DBFILENAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE records
                SET change_date=?, content=?
                WHERE type='A' and name=?;
            """, (now, self.client_address[0], DOMAIN))
            print(cursor.rowcount)
            soa = SOA_CONTENT.format(now)
            cursor.execute("""
                UPDATE records 
                SET change_date=?, content=?
                WHERE type='SOA' and name=?;
            """, (now, soa, DOMAIN))
            print(cursor.rowcount)
            conn.commit()



    def do_GET(self):
        ''' Present frontpage with user authentication. '''
        parsed_path = parse.urlparse(self.path)
        message_parts = [
            'CLIENT VALUES:',
            'client_address={} ({})'.format(
                self.client_address,
                self.address_string()),
            'command={}'.format(self.command),
            'path={}'.format(self.path),
            'real path={}'.format(parsed_path.path),
            'query={}'.format(parsed_path.query),
            'request_version={}'.format(self.request_version),
            '',
            'SERVER VALUES:',
            'server_version={}'.format(self.server_version),
            'sys_version={}'.format(self.sys_version),
            'protocol_version={}'.format(self.protocol_version),
            '',
            'HEADERS RECEIVED:',
        ]
        for name, value in sorted(self.headers.items()):
            message_parts.append(
                '{}={}'.format(name, value.rstrip())
            )
        message_parts.append('')
        message = '\r\n'.join(message_parts)

        if parsed_path.path != '/':
            self.send_error(404)
            return

        if self.headers['Authorization'] is None:
            self.do_AUTHHEAD()
            self.wfile.write('No auth header received'.encode('utf-8'))
        elif not self.check_authentication():
            return
        else:
            self.update_dns()
            self.do_HEAD()
            self.wfile.write(message.encode('utf-8'))


def main():
    """ Main dyndns server function """

    if not os.path.exists(DBFILENAME):
        print("Datebase file {} does not exists".format(DBFILENAME))
        return

    try:
        httpd = CustomServer(
            (SERVERIP, SERVERPORT),
            CustomHandler,
            login=LOGIN, password=PASSWORD)
        print('started httpd...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        httpd.socket.close()

if __name__ == '__main__':
    main()
