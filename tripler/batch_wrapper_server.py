from __future__ import annotations

import argparse
import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

logger = logging.getLogger("batch-wrapper")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class StoredFile:
    id: str
    object: str
    bytes: int
    created_at: int
    filename: str
    purpose: str


@dataclass
class StoredBatch:
    id: str
    object: str
    created_at: int
    status: str
    endpoint: str
    input_file_id: str
    completion_window: str
    output_file_id: str | None
    error_file_id: str | None
    errors: Any


class Storage:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.files_dir = root_dir / "files"
        self.file_meta_dir = root_dir / "file_meta"
        self.batches_dir = root_dir / "batches"

        self.files_dir.mkdir(parents=True, exist_ok=True)
        self.file_meta_dir.mkdir(parents=True, exist_ok=True)
        self.batches_dir.mkdir(parents=True, exist_ok=True)

    def _file_bin_path(self, file_id: str) -> Path:
        return self.files_dir / f"{file_id}.bin"

    def _file_meta_path(self, file_id: str) -> Path:
        return self.file_meta_dir / f"{file_id}.json"

    def _batch_meta_path(self, batch_id: str) -> Path:
        return self.batches_dir / f"{batch_id}.json"

    def save_uploaded_file(self, upload: UploadFile, raw_bytes: bytes, purpose: str) -> StoredFile:
        file_id = f"file-{uuid.uuid4().hex}"
        created_at = int(datetime.now(timezone.utc).timestamp())
        record = StoredFile(
            id=file_id,
            object="file",
            bytes=len(raw_bytes),
            created_at=created_at,
            filename=upload.filename or "upload.bin",
            purpose=purpose,
        )

        self._file_bin_path(file_id).write_bytes(raw_bytes)
        self._file_meta_path(file_id).write_text(json.dumps(asdict(record), indent=2), encoding="utf-8")
        return record

    def read_file_bytes(self, file_id: str) -> bytes:
        path = self._file_bin_path(file_id)
        if not path.exists():
            raise FileNotFoundError(file_id)
        return path.read_bytes()

    def save_file_from_text(self, text: str, filename: str, purpose: str = "batch_result") -> StoredFile:
        file_id = f"file-{uuid.uuid4().hex}"
        created_at = int(datetime.now(timezone.utc).timestamp())
        raw_bytes = text.encode("utf-8")
        record = StoredFile(
            id=file_id,
            object="file",
            bytes=len(raw_bytes),
            created_at=created_at,
            filename=filename,
            purpose=purpose,
        )

        self._file_bin_path(file_id).write_bytes(raw_bytes)
        self._file_meta_path(file_id).write_text(json.dumps(asdict(record), indent=2), encoding="utf-8")
        return record

    def get_file_meta(self, file_id: str) -> StoredFile:
        path = self._file_meta_path(file_id)
        if not path.exists():
            raise FileNotFoundError(file_id)
        return StoredFile(**json.loads(path.read_text(encoding="utf-8")))

    def create_batch(self, input_file_id: str, endpoint: str, completion_window: str) -> StoredBatch:
        batch_id = f"batch-{uuid.uuid4().hex}"
        created_at = int(datetime.now(timezone.utc).timestamp())
        record = StoredBatch(
            id=batch_id,
            object="batch",
            created_at=created_at,
            status="in_progress",
            endpoint=endpoint,
            input_file_id=input_file_id,
            completion_window=completion_window,
            output_file_id=None,
            error_file_id=None,
            errors=None,
        )
        self._batch_meta_path(batch_id).write_text(json.dumps(asdict(record), indent=2), encoding="utf-8")
        return record

    def update_batch(self, batch: StoredBatch) -> None:
        self._batch_meta_path(batch.id).write_text(json.dumps(asdict(batch), indent=2), encoding="utf-8")

    def get_batch(self, batch_id: str) -> StoredBatch:
        path = self._batch_meta_path(batch_id)
        if not path.exists():
            raise FileNotFoundError(batch_id)
        return StoredBatch(**json.loads(path.read_text(encoding="utf-8")))


def create_app(upstream_base_url: str, storage_dir: str) -> FastAPI:
    app = FastAPI(title="vLLM Batch Wrapper", version="0.1.0")
    storage = Storage(Path(storage_dir))

    async def run_single_request(client: httpx.AsyncClient, line: dict[str, Any]) -> dict[str, Any]:
        custom_id = str(line.get("custom_id", ""))
        method = str(line.get("method", "POST")).upper()
        url = str(line.get("url", ""))
        body = line.get("body", {})

        if method != "POST":
            return {
                "custom_id": custom_id,
                "error": {
                    "type": "unsupported_method",
                    "message": f"Only POST is supported, got {method}",
                },
            }

        if url != "/v1/chat/completions":
            return {
                "custom_id": custom_id,
                "error": {
                    "type": "unsupported_url",
                    "message": f"Only /v1/chat/completions is supported, got {url}",
                },
            }

        try:
            response = await client.post(url, json=body)
            response_json = response.json()
            if response.status_code >= 400:
                return {
                    "custom_id": custom_id,
                    "error": {
                        "type": "upstream_http_error",
                        "status_code": response.status_code,
                        "message": response_json,
                    },
                }
            return {
                "id": f"batch_req-{uuid.uuid4().hex}",
                "custom_id": custom_id,
                "response": {
                    "status_code": response.status_code,
                    "request_id": response.headers.get("x-request-id", ""),
                    "body": response_json,
                },
                "error": None,
            }
        except Exception as exc:
            return {
                "custom_id": custom_id,
                "error": {
                    "type": "upstream_exception",
                    "message": str(exc),
                },
            }

    async def process_batch(batch_id: str) -> None:
        try:
            batch = storage.get_batch(batch_id)
            input_bytes = storage.read_file_bytes(batch.input_file_id)
            lines = [line.strip() for line in input_bytes.decode("utf-8").splitlines() if line.strip()]
            requests_payload = [json.loads(line) for line in lines]

            timeout = httpx.Timeout(120.0, connect=10.0)
            async with httpx.AsyncClient(base_url=upstream_base_url, timeout=timeout) as client:
                max_concurrency = 100
                indexed_requests: asyncio.Queue[tuple[int, dict[str, Any]]] = asyncio.Queue()
                for idx, req in enumerate(requests_payload):
                    indexed_requests.put_nowait((idx, req))

                results: list[dict[str, Any] | None] = [None] * len(requests_payload)

                async def worker() -> None:
                    while True:
                        try:
                            idx, req = indexed_requests.get_nowait()
                        except asyncio.QueueEmpty:
                            return
                        try:
                            results[idx] = await run_single_request(client, req)
                        finally:
                            indexed_requests.task_done()

                worker_count = min(max_concurrency, len(requests_payload))
                if worker_count > 0:
                    workers = [asyncio.create_task(worker()) for _ in range(worker_count)]
                    await indexed_requests.join()
                    await asyncio.gather(*workers)

                final_results = [result for result in results if result is not None]

            output_jsonl = "\n".join(json.dumps(result, ensure_ascii=False) for result in final_results) + "\n"
            output_file = storage.save_file_from_text(
                text=output_jsonl,
                filename=f"{batch_id}_output.jsonl",
                purpose="batch_output",
            )

            batch.status = "completed"
            batch.output_file_id = output_file.id
            batch.errors = None
            storage.update_batch(batch)
            logger.info("Batch %s completed with %d requests", batch_id, len(final_results))
        except Exception as exc:
            logger.exception("Batch %s failed: %s", batch_id, exc)
            batch = storage.get_batch(batch_id)
            batch.status = "failed"
            batch.errors = {
                "object": "list",
                "data": [
                    {
                        "code": "batch_processing_error",
                        "message": str(exc),
                        "param": None,
                        "line": None,
                    }
                ],
            }
            storage.update_batch(batch)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "time": utc_now_iso()}

    @app.post("/v1/files")
    async def create_file(file: UploadFile = File(...), purpose: str = Form(...)) -> dict[str, Any]:
        raw_bytes = await file.read()
        record = storage.save_uploaded_file(upload=file, raw_bytes=raw_bytes, purpose=purpose)
        return asdict(record)

    @app.get("/v1/files/{file_id}")
    def retrieve_file(file_id: str) -> dict[str, Any]:
        try:
            record = storage.get_file_meta(file_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=f"File not found: {exc}") from exc
        return asdict(record)

    @app.get("/v1/files/{file_id}/content")
    def file_content(file_id: str) -> Response:
        try:
            content = storage.read_file_bytes(file_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=f"File not found: {exc}") from exc
        return Response(content=content, media_type="application/octet-stream")

    @app.post("/v1/batches")
    async def create_batch(payload: dict[str, Any]) -> dict[str, Any]:
        input_file_id = str(payload.get("input_file_id", ""))
        endpoint = str(payload.get("endpoint", ""))
        completion_window = str(payload.get("completion_window", "24h"))

        if not input_file_id:
            raise HTTPException(status_code=400, detail="input_file_id is required")
        if endpoint != "/v1/chat/completions":
            raise HTTPException(status_code=400, detail="Only /v1/chat/completions is supported")

        try:
            storage.get_file_meta(input_file_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=f"Input file not found: {exc}") from exc

        batch = storage.create_batch(
            input_file_id=input_file_id,
            endpoint=endpoint,
            completion_window=completion_window,
        )

        asyncio.create_task(process_batch(batch.id))
        return asdict(batch)

    @app.get("/v1/batches/{batch_id}")
    def retrieve_batch(batch_id: str) -> dict[str, Any]:
        try:
            batch = storage.get_batch(batch_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=f"Batch not found: {exc}") from exc
        return asdict(batch)

    return app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wrapper adding OpenAI files/batches endpoints for vLLM")
    parser.add_argument(
        "--upstream-base-url",
        default="http://localhost:8001",
        help="Base URL of upstream vLLM OpenAI-compatible server (without /v1 suffix)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for wrapper server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8010,
        help="Port for wrapper server",
    )
    parser.add_argument(
        "--storage-dir",
        default=".batch_wrapper_data",
        help="Directory used for persisted files and batch metadata",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    import uvicorn

    app = create_app(
        upstream_base_url=args.upstream_base_url,
        storage_dir=args.storage_dir,
    )

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
