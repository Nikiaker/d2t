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
    
    # Process each domain
    for domain in domains:
        # Create domain output folder
        output_dir = f"./outputs/{domain}_output"
        Path(output_dir).mkdir(exist_ok=True)
        
        # Set environment variable and run extraction
        os.environ["WEBNLG_DOMAIN"] = domain
        print(f"Processing domain: {domain}")
        extract_triples(f"./{output_dir}/predicates_{domain}.txt")

        # Read predicates from file
        with open(f"./{output_dir}/predicates_{domain}.txt", "r") as f:
            predicates_text = f.read()

        # Copy templates folder
        templates_src = "./templates"
        templates_dst = f"{output_dir}/templates"
        if os.path.exists(templates_dst):
            shutil.rmtree(templates_dst)
        shutil.copytree(templates_src, templates_dst)
        
        # Copy config_remote.yaml
        shutil.copy("./config_remote.yaml", f"{output_dir}/config_remote.yaml")
        
        # Update system_message.txt with domain and triples
        system_message_path = f"{templates_dst}/system_message.txt"
        with open(system_message_path, "r") as f:
            system_message = f.read()
        
        system_message = system_message.replace("{domain}", domain)
        system_message = system_message.replace("{triples}", predicates_text)
        
        with open(system_message_path, "w") as f:
            f.write(system_message)
        
        # Update config_remote.yaml template_dir path
        config_path = f"{output_dir}/config_remote.yaml"
        with open(config_path, "r") as f:
            config_content = f.read()
        
        config_content = config_content.replace(
            'template_dir: "./templates/"',
            f'template_dir: "{output_dir}/templates/"'
        )
        
        with open(config_path, "w") as f:
            f.write(config_content)
        
