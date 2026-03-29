import argparse
import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

from openai import OpenAI

from app import (
    Triple,
    parse_batch_output,
    read_openai_file_text,
)

logger = logging.getLogger(__name__)


def cmd_extract(args: argparse.Namespace) -> None:
    """Extract triples from a file_id (batch output file)."""
    logger.info("OpenAI base URL: %s", args.base_url)
    logger.info("File ID: %s", args.file_id)

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    logger.info("Reading file from OpenAI...")
    output_text = read_openai_file_text(client=client, file_id=args.file_id)

    logger.info("Parsing batch output...")
    triples_by_instance_id = parse_batch_output(output_text)

    all_triples: list[Triple] = []
    triples_by_instance: list[dict[str, Any]] = []
    
    for instance_id in sorted(triples_by_instance_id.keys()):
        triples = triples_by_instance_id[instance_id]
        all_triples.extend(triples)
        triples_by_instance.append({
            "instance_id": instance_id,
            "triples": [asdict(t) for t in triples],
        })

    unique_predicates = list(dict.fromkeys(t.predicate for t in all_triples))

    logger.info("Loaded %d triples from file %s (unique predicates: %d)", 
                len(all_triples), args.file_id, len(unique_predicates))

    extraction_output = {
        "source_file_id": args.file_id,
        "instances_count": len(triples_by_instance),
        "triples_count": len(all_triples),
        "unique_predicates": unique_predicates,
        "triples_by_instance": triples_by_instance,
        "all_triples": [asdict(t) for t in all_triples],
    }

    Path(args.output).write_text(
        json.dumps(extraction_output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Extraction complete. Results saved to %s", args.output)


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Extract and parse triples from an OpenAI file (batch output)."
    )
    parser.add_argument("--file-id", required=True, help="OpenAI file ID to read and parse")
    parser.add_argument("--output", required=True, help="Path to output triples")
    parser.add_argument("--base-url", default="http://localhost:8000/v1", help="OpenAI-compatible base URL")
    parser.add_argument("--api-key", default="local-key", help="API key value accepted by the local server")

    args = parser.parse_args()
    cmd_extract(args)


if __name__ == "__main__":
    main()
