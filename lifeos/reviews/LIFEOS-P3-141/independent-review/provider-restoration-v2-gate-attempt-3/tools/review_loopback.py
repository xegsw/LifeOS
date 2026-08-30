#!/usr/bin/env python3
"""Synthetic-only Custom OpenAI-compatible loopback for attempt-3."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port-file", required=True)
    parser.add_argument("--receipt-file", required=True)
    parser.add_argument("--max-requests", type=int, default=2)
    args = parser.parse_args()
    receipt = Path(args.receipt_file)
    events: list[dict[str, object]] = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, _format: str, *_args: object) -> None:
            return

        def send_json(self, status: int, payload: object) -> None:
            raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(raw)

        def capture(self) -> None:
            events.append({"method": self.command, "path": self.path, "content_length": int(self.headers.get("Content-Length", "0")), "authorization_present": bool(self.headers.get("Authorization"))})
            receipt.write_text(json.dumps({"schema": "lifeos.p3-141.review-loopback.v1", "events": events, "synthetic_only": True, "request_content_recorded": False}, indent=2) + "\n", encoding="utf-8")

        def do_GET(self) -> None:
            self.capture()
            if self.path == "/fixture/v1/models":
                self.send_json(200, {"object": "list", "data": [{"id": "fixture-model", "object": "model"}]})
            else:
                self.send_json(404, {"error": "fixture path rejected"})
            self.finish_if_ready()

        def do_POST(self) -> None:
            self.capture()
            if self.path == "/fixture/v1/chat/completions":
                inner = json.dumps({"kind": "suggestion", "summary": "synthetic custom loopback result", "uncertainty": "synthetic_fixture", "evidence_refs": ["capture:synthetic"]}, separators=(",", ":"))
                self.send_json(200, {"choices": [{"message": {"content": inner}}]})
            else:
                self.send_json(404, {"error": "fixture path rejected"})
            self.finish_if_ready()

        def finish_if_ready(self) -> None:
            if len(events) >= args.max_requests:
                self.server.should_stop = True

    server = HTTPServer(("127.0.0.1", 0), Handler)
    Path(args.port_file).write_text(str(server.server_port) + "\n", encoding="utf-8")
    while not getattr(server, "should_stop", False):
        server.handle_request()


if __name__ == "__main__":
    main()
