# This script will generate the base files for a new Ansible role based on user input.
#
# Usage: python new_role.py
# Then follow on-screen prompts.

import os
from jinja2 import Environment, FileSystemLoader


# Change working directory to script's directory
dirname = os.path.dirname(os.path.realpath(__file__))
os.chdir(dirname)

print()
print("=== New Role Generator ===")
print("This script will ask you a series of questions to generate a new role.")
print(
    "It cannot do everything automatically, but it will create the base files for you."
)
print(
    "For example, if your app needs multiple Docker container, just enter the main one here,"
)
print("then modify the generated files later to add the additional containers.")
print()

# Gather information
full_name = input("Enter the full name of the role: ")
default_short_name = full_name.lower().replace(" ", "_").replace("-", "_")
short_name = input(
    f"Enter the short name of the role (lowercase no spaces or dashes, default: `{default_short_name}`): "
)
if short_name.strip() == "":
    short_name = default_short_name
else:
    short_name = short_name.lower().replace(" ", "_").replace("-", "_")

while True:
    docker_container = input(
        "Enter the Docker container image name (e.g. `portainer/portainer-ce`): "
    )
    if docker_container.strip() != "":
        break

docker_tag = input("Enter the Docker container tag (Default: 'latest'): ")
if docker_tag.strip() == "":
    docker_tag = "latest"

has_directories = input("Does the app need data directories (Y/n): ")
has_directories = has_directories.lower() != "n"

default_port = input("Enter the default port the app uses (or leave blank if none): ")
if default_port.strip() == "":
    default_port = None

if default_port is not None:
    has_web_interface = input("Does the app have a web interface (Y/n): ")
    network_enabled = has_web_interface.lower() != "n"

    has_docker_network = input("Does the app need Docker network (y/N): ")
    has_docker_network = has_docker_network.lower() == "y"
else:
    network_enabled = False
    has_docker_network = False


env = Environment(loader=FileSystemLoader("./templates"), trim_blocks=True)
defaults_template = env.get_template("defaults.yml.j2")
tasks_template = env.get_template("tasks.yml.j2")
docs_template = env.get_template("docs.mdx.j2")
filename_map = {
    "defaults.yml.j2": f"../roles/{short_name}/defaults/main.yml",
    "tasks.yml.j2": f"../roles/{short_name}/tasks/main.yml",
    "docs.mdx.j2": f"../docs/src/content/docs/applications/{short_name}.mdx",
}
for template in [defaults_template, tasks_template, docs_template]:
    output_from_parsed_template = template.render(
        full_name=full_name,
        short_name=short_name,
        has_directories=has_directories,
        default_port=default_port,
        network_enabled=network_enabled,
        has_docker_network=has_docker_network,
        docker_container=docker_container,
        docker_tag=docker_tag,
    )
    output_filename = filename_map[template.name]
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, "w") as file:
        file.write(output_from_parsed_template)
    print(f"Generated {output_filename}")

print()
print("Role generation complete!")
print("Please review and modify the generated files as necessary to fit your application's needs.")
print()
print("Now, please add the following to playbook.yml alphabetically to include the new role:")
print()
print(f"    - role: {short_name}")
print(f"      tags: {short_name}")
print(f"      when: {short_name}_enabled or ({short_name}_container_names | intersect(running_containers) | length > 0)")
print()
print("Don't forget to run linting and tests once you're done to ensure everything is set up correctly!")