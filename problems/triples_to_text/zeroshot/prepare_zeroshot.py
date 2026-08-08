import json
import os
from pathlib import Path


def get_ports(index: int) -> tuple[int, int, int, int]:
    base_port = 3200 + index * 4
    return base_port, base_port + 1, base_port + 2, base_port + 3


def main():
    domains_path = "./webnlg_domains.json"
    with open(domains_path, "r") as f:
        webnlg_domains = json.load(f)

    domains: list[str] = webnlg_domains["domains"]

    template_path = "./zeroshot/batch_template.sh"
    with open(template_path, "r") as f:
        template = f.read()

    run_all: list[str] = []
    output_dir = Path("./outputs/zeroshot")
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, domain in enumerate(domains):
        domain_output = output_dir / f"{domain}_output"
        domain_output.mkdir(parents=True, exist_ok=True)

        port_0, port_1, port_2, port_3 = get_ports(i)

        batch_script = (
            template.replace("{port_0}", str(port_0))
            .replace("{port_1}", str(port_1))
            .replace("{port_2}", str(port_2))
            .replace("{port_3}", str(port_3))
            .replace("{domain}", domain)
        )

        batch_script_path = domain_output / f"{domain}.sh"
        with open(batch_script_path, "w") as f:
            f.write(batch_script)

        run_all.append(
            f"sbatch $D2TPATH/problems/triples_to_text/outputs/zeroshot/{domain}_output/{domain}.sh"
        )

    run_all_path = output_dir / "run_all.sh"
    with open(run_all_path, "w") as f:
        f.write("\n".join(run_all) + "\n")

    print(f"Prepared {len(domains)} domain jobs in {output_dir.resolve()}")
    print(f"Batch submit: {run_all_path}")


if __name__ == "__main__":
    main()
