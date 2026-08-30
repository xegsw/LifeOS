#!/usr/bin/env python3
"""Review-owned loopback-only model discovery fixture; never proxies externally."""
import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path("/private/tmp/lifeos-p3-141-provider-restoration-v2-ui-key-direct-pid-review-v1").resolve()
LOG = ROOT / "loopback-model-fixture-requests.jsonl"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def do_GET(self):
        record = {"method": "GET", "path": self.path, "content_length": self.headers.get("Content-Length", "0")}
        with LOG.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True) + "\n")
        if self.path == "/v1/models":
            body = json.dumps({"object": "list", "data": [{"id": "review-fixture-model", "object": "model"}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        # The only request body this fixture accepts is this review's synthetic
        # OpenAI-compatible envelope.  It derives the opaque synthetic Evidence
        # reference and never records request content.
        try:
            payload = json.loads(raw)
            messages = payload.get("messages", [])
            joined = "\n".join(str(item.get("content", "")) for item in messages if isinstance(item, dict))
            matched = re.search(r"capture:capture:p3-141:synthetic:[A-Za-z0-9:-]+", joined)
            evidence_ref = matched.group(0) if matched else None
        except (ValueError, TypeError):
            evidence_ref = None
        with LOG.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"method": "POST", "path": self.path, "content_length": str(length), "synthetic_evidence_ref_accepted": bool(evidence_ref)}, sort_keys=True) + "\n")
        if self.path != "/v1/chat/completions" or not evidence_ref:
            self.send_response(400)
            self.end_headers()
            return
        inner = {"kind": "suggestion", "summary": "review loopback synthetic recommendation", "uncertainty": "synthetic_fixture", "evidence_refs": [evidence_ref]}
        body = json.dumps({"choices": [{"message": {"content": json.dumps(inner, separators=(",", ":"))}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print("review_loopback_fixture_ready=127.0.0.1:11434", flush=True)
    HTTPServer(("127.0.0.1", 11434), Handler).serve_forever()
