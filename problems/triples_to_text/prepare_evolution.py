import json
import os
import shutil
from pathlib import Path
from tests.dataset_multi_predicates import extract_triples

if __name__ == "__main__":
    # Load domains from JSON
    with open("./webnlg_domains.json", "r") as f:
        webnlg_domains = json.load(f)
    
    domains: list[str] = webnlg_domains["domains"]
    evolution_configs: list[str] = webnlg_domains["configs"]

    Path("./outputs").mkdir(exist_ok=True)

    run_all: list[str] = []

    # Process each config and domain pair
    for evolution_config in evolution_configs:
        config_dir = f"./configs/{evolution_config}"
        config_template_path = f"{config_dir}/config_remote.yaml"
        batch_template_path = f"{config_dir}/batch_template.sh"

        for domain in domains:
            # Create domain output folder under config folder
            output_dir = f"./outputs/{evolution_config}/{domain}_output"
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Set environment variable and run extraction
            os.environ["WEBNLG_DOMAIN"] = domain
            print(f"Processing config={evolution_config}, domain={domain}")
            extract_triples(f"{output_dir}/predicates_{domain}.txt")

            # Read predicates from file
            with open(f"{output_dir}/predicates_{domain}.txt", "r") as f:
                predicates_text = f.read()

            # Copy templates folder
            templates_src = "./templates"
            templates_dst = f"{output_dir}/templates"
            if os.path.exists(templates_dst):
                shutil.rmtree(templates_dst)
            shutil.copytree(templates_src, templates_dst)

            # Copy config-specific files
            shutil.copy(config_template_path, f"{output_dir}/config_remote.yaml")
            shutil.copy(batch_template_path, f"{output_dir}/{domain}.sh")

            # Update system_message.txt with domain and triples
            system_message_path = f"{templates_dst}/system_message.txt"
            with open(system_message_path, "r") as f:
                system_message = f.read()

            system_message = system_message.replace("{domain}", domain)
            system_message = system_message.replace("{triples}", predicates_text)

            with open(system_message_path, "w") as f:
                f.write(system_message)

            # Update batch template with domain and config name
            batch_script_path = f"{output_dir}/{domain}.sh"
            with open(batch_script_path, "r") as f:
                batch_script_content = f.read()

            batch_script_content = batch_script_content.replace("{domain}", domain)
            batch_script_content = batch_script_content.replace("{evolution_config}", evolution_config)

            with open(batch_script_path, "w") as f:
                f.write(batch_script_content)

            # Update config db path for the nested output directory
            config_path = f"{output_dir}/config_remote.yaml"
            with open(config_path, "r") as f:
                config_content = f.read()

            config_content = config_content.replace(
                'db_path: "./all_programs/"',
                f'db_path: "./outputs/{evolution_config}/{domain}_output/all_programs/"'
            )

            with open(config_path, "w") as f:
                f.write(config_content)

            run_all.append(
                f"sbatch ~/d2t/problems/triples_to_text/outputs/{evolution_config}/{domain}_output/{domain}.sh"
            )

    with open("./run_all.sh", "w") as f:
        f.writelines("\n".join(run_all))
