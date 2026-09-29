"""Request-body boundary checks shared by the two local AI workspaces."""
import io
import json
import unittest
from local_host import Handler


class HostProbe:
    def __init__(self, payload):
        self.headers = {'Content-Length': str(len(payload)), 'Content-Type': 'application/json'}
        self.rfile = io.BytesIO(payload)
        self.path = '/api/documents'
        self.dispatched = None
        self.status = None

    def allowed(self):
        return True

    def post_api(self, path, body):
        self.dispatched = body
        return self.send({'ok': True})

    def send(self, body, status=200):
        self.status = status
        return body


class HostLimitTests(unittest.TestCase):
    def test_accepts_maximum_document_length_with_multibyte_unicode(self):
        text = '漢' * 120000
        payload = json.dumps({'text': text, 'title': 'Unicode source', 'source': 'local'}, ensure_ascii=False).encode('utf-8')
        self.assertGreater(len(payload), 300000)
        probe = HostProbe(payload)
        Handler.do_POST(probe)
        self.assertEqual(probe.status, 200)
        self.assertEqual(probe.dispatched['text'], text)

    def test_rejects_body_above_one_million_bytes(self):
        probe = HostProbe(b' ' * 1000001)
        Handler.do_POST(probe)
        self.assertEqual(probe.status, 400)
        self.assertIsNone(probe.dispatched)


if __name__ == '__main__':
    unittest.main()
