"""Small local-only HTTP host; no third-party runtime dependencies."""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json, mimetypes, os
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent
class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup(); self.connection.settimeout(10)
    def log_message(self, *args): pass
    def send(self, data, status=200, content_type='application/json; charset=utf-8', download=None):
        if not isinstance(data, (bytes,str)): data=json.dumps(data,ensure_ascii=False)
        if isinstance(data,str): data=data.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type',content_type)
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'")
        if download:self.send_header('Content-Disposition',f'attachment; filename="{download}"')
        self.end_headers(); self.wfile.write(data)
    def allowed(self):
        authority=self.headers.get('Host','')
        allowed={f'localhost:{self.server.server_port}',f'127.0.0.1:{self.server.server_port}'}
        origin=self.headers.get('Origin')
        return authority in allowed and (not origin or origin in {'http://'+h for h in allowed})
    def do_GET(self):
        if not self.allowed():return self.send({'error':'Local access only'},403)
        path=urlsplit(self.path).path
        if path.startswith('/api/'):
            try:return self.get_api(path)
            except ValueError as e:return self.send({'error':str(e)},400)
            except Exception:return self.send({'error':'The request could not be completed.'},500)
        targets={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}
        if path not in targets:return self.send({'error':'Not found'},404)
        p=ROOT/'static'/targets[path]
        return self.send(p.read_bytes(),content_type=mimetypes.guess_type(p)[0]+'; charset=utf-8')
    def do_POST(self):
        if not self.allowed():return self.send({'error':'Local access only'},403)
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=1000000:raise ValueError('Request must be between 1 and 1000000 bytes.')
            if self.headers.get('Content-Type','').split(';')[0]!='application/json':raise ValueError('JSON request required.')
            body=json.loads(self.rfile.read(size))
            if not isinstance(body,dict):raise ValueError('JSON object required.')
            return self.post_api(urlsplit(self.path).path,body)
        except (ValueError,KeyError,TypeError) as e:return self.send({'error':str(e)},400)
        except Exception:return self.send({'error':'The request could not be completed.'},500)
def field(body,key,limit=10000):
    value=body.get(key,'')
    if not isinstance(value,str) or not value.strip() or len(value)>limit:raise ValueError(f'{key}: enter 1–{limit} characters.')
    return value.strip()
def serve(handler,port):
    port=int(os.environ.get('PORT',port))
    server=ThreadingHTTPServer(('127.0.0.1',port),handler)
    server.daemon_threads=True
    print(f'Open http://127.0.0.1:{port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:server.server_close()
