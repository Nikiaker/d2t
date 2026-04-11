import argparse
import json
import logging
from pathlib import Path

from openai import OpenAI

from app import extract_instances
from predicate_domain_workflow import run_domain_predicate_workflow

logger = logging.getLogger(__name__)


def cmd_extract(args: argparse.Namespace) -> None:
    logger.info("OpenAI base URL: %s", args.base_url)
    logger.info("Model: %s", args.model)
    logger.info("Domain: %s", args.domain)

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    instances = extract_instances(payload)
    logger.info("Extracted %d instances from input JSON", len(instances))

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)
    output = run_domain_predicate_workflow(
        client=client,
        model=args.model,
        domain=args.domain,
        instances=instances,
        max_expansion_rounds=args.max_expansion_rounds,
        logger=logger,
    )

    Path(args.output).write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Workflow complete. Results saved to %s", args.output)


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Domain-aware semantic triple extraction with adaptive predicate inventory."
    )
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", required=True, help="Path to output results")
    parser.add_argument("--domain", required=True, help="Problem domain, e.g. weather forecast")
    parser.add_argument("--model", required=True, help="Model name served by vLLM/OpenAI-compatible API")
    parser.add_argument("--base-url", default="http://localhost:8000/v1", help="OpenAI-compatible base URL")
    parser.add_argument("--api-key", default="local-key", help="API key value accepted by the local server")
    parser.add_argument(
        "--max-expansion-rounds",
        type=int,
        default=3,
        help="Max predicate-expansion retries per instance",
    )

    args = parser.parse_args()
    cmd_extract(args)


if __name__ == "__main__":
    main()