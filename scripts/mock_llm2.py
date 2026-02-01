#!/usr/bin/env python3

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


HELLO_TEXT = "Hello LLM!"


class OpenAIMockHandler(BaseHTTPRequestHandler):
	server_version = "openai-mock/0.2"

	def _send_json(self, status_code: int, payload: dict) -> None:
		data = json.dumps(payload).encode("utf-8")
		self.send_response(status_code)
		self.send_header("Content-Type", "application/json")
		self.send_header("Content-Length", str(len(data)))
		self.end_headers()
		self.wfile.write(data)

	def do_POST(self):  # noqa: N802
		if self.path not in ("/v1/chat/completions", "/v1/completions"):
			self._send_json(
				404,
				{
					"error": {
						"message": "Not found",
						"type": "invalid_request_error",
						"param": None,
						"code": "not_found",
					},
				},
			)
			return

		content_length = int(self.headers.get("Content-Length", "0") or "0")
		body = self.rfile.read(content_length) if content_length > 0 else b"{}"
		try:
			request_json = json.loads(body.decode("utf-8")) if body else {}
		except json.JSONDecodeError:
			request_json = {}

		# Minimal OpenAI-style responses for /v1/chat/completions and /v1/completions
		now = int(time.time())
		model = request_json.get("model") or "mock-model"
		if self.path == "/v1/chat/completions":
			payload = {
				"id": "chatcmpl-mock",
				"object": "chat.completion",
				"created": now,
				"model": model,
				"choices": [
					{
						"index": 0,
						"message": {"role": "assistant", "content": HELLO_TEXT},
						"finish_reason": "stop",
					}
				],
				"usage": {
					"prompt_tokens": 0,
					"completion_tokens": 0,
					"total_tokens": 0,
				},
			}
		else:
			payload = {
				"id": "cmpl-mock",
				"object": "text_completion",
				"created": now,
				"model": model,
				"choices": [
					{
						"text": HELLO_TEXT,
						"index": 0,
						"logprobs": None,
						"finish_reason": "stop",
					}
				],
				"usage": {
					"prompt_tokens": 0,
					"completion_tokens": 0,
					"total_tokens": 0,
				},
			}
		self._send_json(200, payload)

	def do_GET(self):  # noqa: N802
		# Helpful health endpoint (not required by OpenAI clients)
		if self.path in ("/", "/health"):
			self._send_json(200, {"status": "ok"})
			return
		self._send_json(404, {"error": {"message": "Not found"}})

	def log_message(self, format, *args):  # noqa: A002
		# Keep stdout clean unless user wants verbose logs.
		return


def main() -> int:
	parser = argparse.ArgumentParser(description="Mock OpenAI /v1/chat/completions and /v1/completions server")
	parser.add_argument("--host", default="127.0.0.1")
	parser.add_argument("--port", type=int, default=8000)
	args = parser.parse_args()

	httpd = ThreadingHTTPServer((args.host, args.port), OpenAIMockHandler)
	print(f"Mock LLM listening on http://{args.host}:{args.port}")
	print("POST /v1/chat/completions -> {choices:[{message:{content:'Hello LLM!'}}]}")
	print("POST /v1/completions -> {choices:[{text:'Hello LLM!'}]}")
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	finally:
		httpd.server_close()
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
