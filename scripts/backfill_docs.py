# This script backfills documentation files for Ansible roles that lack them.
#
# Usage: python backfill_docs.py

import os
from jinja2 import Environment, FileSystemLoader
import yaml


# Change working directory to script's directory
dirname = os.path.dirname(os.path.realpath(__file__))
os.chdir(dirname)


all_roles = os.listdir("../roles")
all_roles.sort()
roles_to_exclude = ["ansible_homelab_orchestration_general", "breaking_changes", "personal"]
roles_to_backfill = [role for role in all_roles if role not in roles_to_exclude]


def load_yaml_file(file_path):
    with open(file_path, "r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)
            return None


env = Environment(loader=FileSystemLoader("./templates"), trim_blocks=True)
docs_template = env.get_template("docs.mdx.j2")

print()
print("Backfilling roles...", end="")

for role in roles_to_backfill:
    if os.path.exists(f"../docs/src/content/docs/applications/{role}.mdx"):
        print(f"Skipping {role}, documentation already exists.")
        continue
    print(f"Generating {role}...")
    defaults_yaml = load_yaml_file(f"../roles/{role}/defaults/main.yml")

    short_name = role
    full_name = input(f"Enter the full name of the role '{role}': ")

    default_port = defaults_yaml.get(f"{short_name}_port", None)
    if default_port is None:
        default_port = defaults_yaml.get(f"{short_name}_http_port", None)
    if default_port is None:
        default_port = input(
            f"Enter the default port for {role} (or leave blank if none): "
        )
        if default_port.strip() == "":
            default_port = None

    output_from_parsed_template = docs_template.render(
        full_name=full_name,
        short_name=short_name,
        default_port=default_port,
    )
    output_filename = f"../docs/src/content/docs/applications/{short_name}.mdx"
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, "w") as file:
        file.write(output_from_parsed_template)
    print(f"Generated {output_filename}")

print()
print("Documentation Backfill complete!")
print("Please Fill in the remaining information in each of the generated .mdx files.")
