import json
import subprocess
import sys
import unittest

from service_closed import app


class ServiceClosedTests(unittest.IsolatedAsyncioTestCase):
    async def request(self, path, method="GET", headers=None):
        sent = []

        async def receive():
            self.fail("Closed services must never read a request body")

        async def send(event):
            sent.append(event)

        await app({"type": "http", "path": path, "method": method,
                   "headers": headers or []}, receive, send)
        return sent[0], sent[1]["body"]

    async def test_all_routes_and_methods_rejected_before_processing(self):
        for path in ("/", "/v1/easytl", "/proxy/easytl", "/auth/login",
                     "/auth/signup", "/admin/db/replace-database", "/financial",
                     "/docs", "/unknown", "/healthz/", "/healthz/../v1/easytl"):
            for method in ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE"):
                with self.subTest(path=path, method=method):
                    response, body = await self.request(path, method, [
                        (b"authorization", b"Bearer anything"),
                        (b"content-length", b"999999999"),
                        (b"content-type", b"application/json"),
                    ])
                    self.assertEqual(response["status"], 410)
                    self.assertEqual(json.loads(body)["error"], "service_closed")
                    self.assertIn("sources", json.loads(body))

    async def test_health_is_only_read_only_exception(self):
        response, body = await self.request("/healthz")
        self.assertEqual(response["status"], 200)
        self.assertEqual(json.loads(body)["service_status"], "closed")
        for method in ("POST", "PUT", "PATCH", "DELETE", "OPTIONS"):
            response, _ = await self.request("/healthz", method)
            self.assertEqual(response["status"], 410)

    async def test_head_has_no_body(self):
        for path, status in (("/", 410), ("/healthz", 200)):
            response, body = await self.request(path, "HEAD")
            self.assertEqual(response["status"], status)
            self.assertEqual(body, b"")

    async def test_cors_and_no_cache(self):
        for origin in (b"https://easytl.org", b"https://kakusui.org"):
            response, _ = await self.request("/proxy/easytl", "POST", [(b"origin", origin)])
            headers = dict(response["headers"])
            self.assertEqual(headers[b"access-control-allow-origin"], origin)
            self.assertEqual(headers[b"cache-control"], b"no-store")
        response, _ = await self.request("/", headers=[(b"origin", b"https://untrusted.example")])
        self.assertNotIn(b"access-control-allow-origin", dict(response["headers"]))

    async def test_websockets_are_closed(self):
        sent = []
        async def send(event):
            sent.append(event)
        await app({"type": "websocket"}, None, send)
        self.assertEqual(sent[0]["code"], 1008)

    async def test_lifespan_runs_without_jobs_or_database(self):
        events = iter([{"type": "lifespan.startup"}, {"type": "lifespan.shutdown"}])
        sent = []
        async def receive():
            return next(events)
        async def send(event):
            sent.append(event["type"])
        await app({"type": "lifespan"}, receive, send)
        self.assertEqual(sent, ["lifespan.startup.complete", "lifespan.shutdown.complete"])

    def test_default_entrypoint_does_not_import_operational_dependencies(self):
        subprocess.run([sys.executable, "-c", (
            "import os, sys; os.environ.pop('HOSTED_SERVICE_CLOSED', None); "
            "import main; assert main.app.__module__ == 'service_closed'; "
            "assert not any(m in sys.modules for m in "
            "('operational_app', 'constants', 'stripe', 'db.base', 'recurrent.scheduler'))"
        )], check=True)


if __name__ == "__main__":
    unittest.main()
