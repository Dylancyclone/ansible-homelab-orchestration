# This script runs tests on all roles to ensure they follow the project's standards.
#
# Usage: python test.py

import os
import re
import sys
import yaml


class bcolors:
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    CYAN = "\033[96m"
    GREY = "\033[90m"
    ENDC = "\033[0m"
    UNDERLINE = "\033[4m"


ERROR_TAG = f"{bcolors.FAIL}[ERROR]{bcolors.ENDC} "
PASS_TAG = f"{bcolors.OKGREEN}[PASS]{bcolors.ENDC} "
INFO_TAG = f"{bcolors.CYAN}[INFO]{bcolors.ENDC} "


def print_color(color, text, newline=True):
    if isinstance(color, list):
        color = "".join(color)
    if newline:
        print(f"{color}{text}{bcolors.ENDC}")
    else:
        print(f"{color}{text}{bcolors.ENDC}", end="")


# Change working directory to project root
dirname = os.path.dirname(os.path.realpath(__file__))
os.chdir(dirname + "/..")

all_roles = os.listdir("./roles")
all_roles.sort()
roles_to_exclude = [
    "ansible_homelab_orchestration_general",
    "breaking_changes",
    "personal",
]
roles_to_test = [role for role in all_roles if role not in roles_to_exclude]


# Things to keep track across roles
role_fails = dict()
cross_role_fail_count = 0
ports_in_use = dict()
hostnames_in_use = dict()


def add_role_fail(role, message, location=""):
    if role not in role_fails:
        role_fails[role] = []
    role_fails[role].append((message, location))


def print_test_result(passed):
    if passed:
        print_color(bcolors.OKGREEN, f".", False)
    else:
        print_color(bcolors.FAIL, f"x", False)


def print_test_skip(problem=False):
    if problem:
        print_color(bcolors.WARNING, f"x", False)
    else:
        print_color(bcolors.GREY, f".", False)


def load_yaml_file(file_path):
    with open(file_path, "r") as f:
        try:
            lines = f.readlines()
            f.seek(0)
            safe_yaml = yaml.safe_load(f)
            return lines, safe_yaml
        except yaml.YAMLError as e:
            print(e)
            return None


def load_raw_file(file_path):
    with open(file_path, "r") as f:
        try:
            lines = f.readlines()
            return lines
        except Exception as e:
            print(e)
            return None


def find_line_number(lines, search_string):
    for i, line in enumerate(lines):
        if search_string in line:
            return i + 1
    return -1


playbook_lines, playbook_yaml = load_yaml_file(f"./playbook.yml")

#
# Tests per role
#
print()
print("Running tests in roles...", end="")

for role in roles_to_test:
    print(f"\n{role} ", end="")
    defaults_lines, defaults_yaml = load_yaml_file(f"./roles/{role}/defaults/main.yml")
    task_lines, task_yaml = load_yaml_file(f"./roles/{role}/tasks/main.yml")
    docs_lines = None

    # Variables to track across defaults and tasks
    has_hostname = False
    container_names_list = None
    container_names_list_is_list = False

    #
    # General Role Tests
    #

    # Role must not have a dash in its name
    test_passed = True
    if "-" in role:
        add_role_fail(
            role,
            f"Role name `{role}` must not contain a dash (`-`). Consider removing or replacing with an underscore (`_`).",
        )
        test_passed = False
    print_test_result(test_passed)

    # Role must be referenced in playbook.yml
    test_passed = True
    role_found_in_playbook = False
    for playbook_role in playbook_yaml[0]["roles"]:
        if playbook_role.get("role", "") == role:
            role_found_in_playbook = True
            break
    if not role_found_in_playbook:
        add_role_fail(
            role,
            f"Role '{role}' not found in playbook.yml",
            "playbook.yml",
        )
        test_passed = False
    print_test_result(test_passed)

    # Role in playbook.yml must have correct tag
    test_passed = True
    role_tag_correct = False
    if not role_found_in_playbook:
        print_test_skip(problem=True)
    else:
        for playbook_role in playbook_yaml[0]["roles"]:
            if playbook_role.get("role", "") == role:
                tags = playbook_role.get("tags", [])
                if role in tags:
                    role_tag_correct = True
                    break
        if not role_tag_correct:
            add_role_fail(
                role,
                f"Role '{role}' does not have correct tag '{role}' in playbook.yml",
                f"playbook.yml:{find_line_number(playbook_lines, role)}",
            )
            test_passed = False
        print_test_result(test_passed)

    # Role in playbook.yml must have correct when condition
    test_passed = True
    role_when_correct = False
    if not role_found_in_playbook:
        print_test_skip(problem=True)
    else:
        for playbook_role in playbook_yaml[0]["roles"]:
            if playbook_role.get("role", "") == role:
                when_condition = playbook_role.get("when", "")
                if (
                    when_condition
                    == f"{role}_enabled or ({role}_container_names | intersect(running_containers) | length > 0)"
                ):
                    role_when_correct = True
                    break
        if not role_when_correct:
            add_role_fail(
                role,
                f"Role '{role}' does not have correct when condition '{role}_enabled' in playbook.yml. Should be: `{role}_enabled or ({role}_container_names | intersect(running_containers) | length > 0)`",
                f"playbook.yml:{find_line_number(playbook_lines, role)}",
            )
            test_passed = False
        print_test_result(test_passed)

    # Role must have a documentation file
    doc_file_path = f"./docs/src/content/docs/applications/{role}.mdx"
    test_passed = True
    if not os.path.exists(doc_file_path):
        add_role_fail(
            role,
            f"Documentation file `{doc_file_path}` not found",
        )
        test_passed = False
    else:
        docs_lines = load_raw_file(f"./docs/src/content/docs/applications/{role}.mdx")
    print_test_result(test_passed)

    #
    # Tests for Documentation file
    #

    if docs_lines is not None:
        # Documentation file must not have any placeholder links
        test_passed = True
        for line in docs_lines:
            if line.startswith("[Repository]({/* REPLACE") or line.startswith(
                "[Homepage]({/* REPLACE"
            ):
                add_role_fail(
                    role,
                    f"Documentation file contains placeholder link: '{line.strip()}'",
                    f"docs/src/content/docs/applications/{role}.mdx:{docs_lines.index(line) + 1}",
                )
                test_passed = False
        print_test_result(test_passed)

        # Documentation must not have a placeholder description
        test_passed = True
        for line in docs_lines:
            if line.startswith("TODO: Add a short description"):
                add_role_fail(
                    role,
                    f"Documentation file contains placeholder description: '{line.strip()}'",
                    f"docs/src/content/docs/applications/{role}.mdx:{docs_lines.index(line) + 1}",
                )
                test_passed = False
        print_test_result(test_passed)

    #
    # Tests for Defaults file
    #

    if defaults_yaml is not None:
        container_names = set()
        container_names_list = defaults_yaml.get(f"{role}_container_names", None)
        directory_names = set()
        # Go through default variables
        for key, value in defaults_yaml.items():
            if key.endswith("_port"):
                ports_in_use[key] = value
            if key.endswith("_hostname"):
                hostnames_in_use[key] = value
            if key.endswith("_directory"):
                directory_names.add(key)
            if key.endswith("_container_name"):
                container_names.add(key)

        # Basic variable presence
        test_passed = True
        # _dns_accessible and _available_externally only needed if _hostname exists
        required_vars = ["enabled", "memory"]
        for var in required_vars:
            if f"{role}_{var}" not in defaults_yaml:
                add_role_fail(
                    role,
                    f"Required variable `{role}_{var}` not found in defaults/main.yml",
                    f"roles/{role}/defaults/main.yml",
                )
                test_passed = False
        print_test_result(test_passed)

        # All port variables must end with _port
        test_passed = True
        for key in defaults_yaml.keys():
            if "_port" in key and not key.endswith("_port"):
                add_role_fail(
                    role,
                    f"Port variable `{key}` must end with `_port`",
                    f"roles/{role}/defaults/main.yml:{find_line_number(defaults_lines, key)}",
                )
                test_passed = False
        print_test_result(test_passed)

        # All directory variables must end with _directory
        test_passed = True
        for key in defaults_yaml.keys():
            if "_directory" in key and not key.endswith("_directory"):
                add_role_fail(
                    role,
                    f"Directory variable `{key}` must end with `_directory`",
                    f"roles/{role}/defaults/main.yml:{find_line_number(defaults_lines, key)}",
                )
                test_passed = False
        print_test_result(test_passed)

        # If hostname present, must have other related vars
        has_hostname = f"{role}_hostname" in defaults_yaml
        if not has_hostname:
            print_test_skip()
        else:
            test_passed = True
            related_vars = ["dns_accessible", "available_externally"]
            for var in related_vars:
                if f"{role}_{var}" not in defaults_yaml:
                    add_role_fail(
                        role,
                        f"`{role}_{var}` not found in defaults/main.yml while `{role}_hostname` is defined",
                        f"roles/{role}/defaults/main.yml",
                    )
                    test_passed = False
            print_test_result(test_passed)

        # container_names_list exists as a list
        container_names_list_is_list = isinstance(container_names_list, list)
        if not container_names_list_is_list:
            add_role_fail(
                role,
                f"`{role}_container_names` is not a list in defaults/main.yml",
                f"roles/{role}/defaults/main.yml",
            )
            print_test_result(False)

        # All container_names must be in container_names_list
        if not container_names_list_is_list:
            print_test_skip(problem=True)
        else:
            test_passed = True
            for container_name in container_names:
                if f"{{{{ {container_name} }}}}" not in container_names_list:
                    add_role_fail(
                        role,
                        f"Container `{container_name}` not found in `{role}_container_names`",
                        f"roles/{role}/defaults/main.yml:{find_line_number(defaults_lines, container_name)}",
                    )
                    test_passed = False
            print_test_result(test_passed)

        # There must not be any container_names_list not in container_names
        if not container_names_list_is_list:
            print_test_skip(problem=True)
        else:
            test_passed = True
            for container_name in container_names_list:
                stripped_name = container_name.replace("{{ ", "").replace(" }}", "")
                if stripped_name not in container_names:
                    add_role_fail(
                        role,
                        f"Container `{stripped_name}` listed in `{role}_container_names` but no matching variable found",
                        f"roles/{role}/defaults/main.yml:{find_line_number(defaults_lines, container_name)}",
                    )
                    test_passed = False
            print_test_result(test_passed)

    #
    # Tests for Task file
    #

    if task_yaml is not None:
        first_block = task_yaml[0]["block"]
        second_block = task_yaml[1]["block"]

        # First task must be checking for Breaking Changes role
        test_passed = True
        task_name = first_block[0].get("name", "")
        first_task_is_breaking_changes = (
            "ansible.builtin.include_role" in first_block[0]
            and first_block[0]["ansible.builtin.include_role"]["name"]
            == "breaking_changes"
        )
        if not first_task_is_breaking_changes:
            add_role_fail(
                role,
                "First task in block must include 'breaking_changes' role",
                f"roles/{role}/tasks/main.yml:{find_line_number(task_lines, task_name)}",
            )
            test_passed = False
        print_test_result(test_passed)

        # First task name must match pattern
        if not first_task_is_breaking_changes:
            print_test_skip(problem=True)
        else:
            test_passed = True
            task_name = first_block[0].get("name", "")
            breaking_changes_pattern = re.compile(
                "^Check for [a-z0-9. _-]+ Breaking Changes$", re.IGNORECASE
            )
            if breaking_changes_pattern.match(first_block[0]["name"]) is None:
                add_role_fail(
                    role,
                    "Name of first task in block must Match 'Check for [app] Breaking Changes'",
                    f"roles/{role}/tasks/main.yml:{find_line_number(task_lines, task_name)}",
                )
                test_passed = False
            print_test_result(test_passed)

        # First task must check current role for breaking changes
        if not first_task_is_breaking_changes:
            print_test_skip(problem=True)
        else:
            test_passed = True
            task_name = first_block[0].get("name", "")
            if (
                "vars" not in first_block[0]
                or first_block[0]["vars"].get("breaking_changes_application", "")
                != role
            ):
                add_role_fail(
                    role,
                    f"First task in block must set 'breaking_changes_application' var to current role name ({role})",
                    f"roles/{role}/tasks/main.yml:{find_line_number(task_lines, task_name)}",
                )
                test_passed = False
            print_test_result(test_passed)

        # Find which task(s) has "community.docker.docker_container"
        docker_start_container_tasks = [
            task for task in first_block if "community.docker.docker_container" in task
        ]
        docker_stop_container_tasks = [
            task for task in second_block if "community.docker.docker_container" in task
        ]

        # If container has network_mode host, add it's traefik port to ports_in_use
        if role != "traefik": # Don't need to worry about traefik colliding with itself
            for docker_task in docker_start_container_tasks:
                if (
                    docker_task["community.docker.docker_container"].get("network_mode", "")
                    == "host"
                ):
                    if "labels" not in docker_task["community.docker.docker_container"]:
                        continue
                    if (
                        f"traefik.http.services.{role}.loadbalancer.server.port"
                        not in docker_task["community.docker.docker_container"].get(
                            "labels", {}
                        )
                    ):
                        continue
                    port_string = (
                        docker_task["community.docker.docker_container"]
                        .get("labels", {})
                        .get(
                            f"traefik.http.services.{role}.loadbalancer.server.port",
                            "",
                        )
                    )
                    if port_string.startswith("{{") and port_string.endswith("}}"):
                        # If the port is a variable, it's already tracked
                        continue
                    else:
                        port = int(port_string)
                    ports_in_use[f"{role} (host mode)"] = port

        # Each docker container task must have a variable name
        if not docker_start_container_tasks:
            print_test_skip()
        else:
            for docker_task in docker_start_container_tasks:
                test_passed = True
                task_name = docker_task.get("name", "")
                image_name = docker_task["community.docker.docker_container"].get(
                    "name", ""
                )
                if not image_name.startswith(f"{{{{ {role}_"):
                    add_role_fail(
                        role,
                        f"Docker container task '{task_name}' does not have a variable container name",
                        f"roles/{role}/tasks/main.yml:{find_line_number(task_lines, task_name)}",
                    )
                    test_passed = False
            print_test_result(test_passed)

        # Each docker container task must have a variable image and tag
        if not docker_start_container_tasks:
            print_test_skip()
        else:
            for docker_task in docker_start_container_tasks:
                test_passed = True
                task_name = docker_task.get("name", "")
                image_name = docker_task["community.docker.docker_container"].get(
                    "image", ""
                )
                image_and_tag_pattern = re.compile(
                    "^{{\\s*" + role + "[a-z_]+\\s*}}:{{\\s*" + role + "[a-z_]+\\s*}}"
                )
                if not image_and_tag_pattern.match(image_name):
                    add_role_fail(
                        role,
                        f"Docker container task '{task_name}' does not have a variable image and tag",
                        f"roles/{role}/tasks/main.yml:{find_line_number(task_lines, task_name)}",
                    )
                    test_passed = False
            print_test_result(test_passed)

        # Each docker container task must have a restart policy of unless-stopped
        if not docker_start_container_tasks:
            print_test_skip()
        else:
            for docker_task in docker_start_container_tasks:
                test_passed = True
                task_name = docker_task.get("name", "")
                if (
                    docker_task["community.docker.docker_container"].get(
                        "restart_policy", ""
                    )
                    != "unless-stopped"
                ):
                    add_role_fail(
                        role,
                        f"Docker container task '{task_name}' does not have a restart policy of 'unless-stopped'",
                        f"roles/{role}/tasks/main.yml:{find_line_number(task_lines, task_name)}",
                    )
                    test_passed = False
            print_test_result(test_passed)

        # Each docker container task must have a memory limit
        if not docker_start_container_tasks:
            print_test_skip()
        else:
            for docker_task in docker_start_container_tasks:
                test_passed = True
                task_name = docker_task.get("name", "")
                if "memory" not in docker_task["community.docker.docker_container"]:
                    add_role_fail(
                        role,
                        f"Docker container task '{task_name}' does not have a memory limit set",
                        f"roles/{role}/tasks/main.yml:{find_line_number(task_lines, task_name)}",
                    )
                    test_passed = False
            print_test_result(test_passed)

        # If hostname is set, at least one docker container must have traefik labels
        has_traefik_label = False
        if not has_hostname:
            print_test_skip()
        else:
            if not docker_start_container_tasks:
                print_test_skip(problem=True)
            else:
                test_passed = False
                for docker_task in docker_start_container_tasks:
                    task_name = docker_task.get("name", "")
                    container_definition = docker_task[
                        "community.docker.docker_container"
                    ]
                    if (
                        "labels" in container_definition
                        and "traefik.enable" in container_definition["labels"]
                    ):
                        has_traefik_label = True
                        test_passed = True
                if not test_passed:
                    add_role_fail(
                        role,
                        f"No docker container task has traefik labels set while hostname is defined",
                        "tasksroles/{role}//main.yml",
                    )
                print_test_result(test_passed)

        # If hostname is set, the traefik.enable label must be set correctly
        if not has_hostname:
            print_test_skip()
        else:
            if not docker_start_container_tasks or not has_traefik_label:
                print_test_skip(problem=True)
            else:
                test_passed = False
                for docker_task in docker_start_container_tasks:
                    task_name = docker_task.get("name", "")
                    container_labels = docker_task[
                        "community.docker.docker_container"
                    ].get("labels", {})
                    if (
                        container_labels.get("traefik.enable", "")
                        == "{{ ("
                        + role
                        + "_dns_accessible or "
                        + role
                        + "_available_externally) | string }}"
                    ):
                        test_passed = True
                if not test_passed:
                    add_role_fail(
                        role,
                        f"`traefik.enable` label not set correctly. Should be `{{{{ ({role}_dns_accessible or {role}_available_externally) | string }}}}`",
                        f"roles/{role}/tasks/main.yml:{find_line_number(task_lines, 'traefik.enable')}",
                    )
                print_test_result(test_passed)

        # If hostname is set, the traefik loadbalancer label must be named correctly
        has_traefik_loadbalancer_label = False
        if not has_hostname:
            print_test_skip()
        else:
            if not docker_start_container_tasks or not has_traefik_label:
                print_test_skip(problem=True)
            else:
                test_passed = False
                for docker_task in docker_start_container_tasks:
                    task_name = docker_task.get("name", "")
                    container_labels = docker_task[
                        "community.docker.docker_container"
                    ].get("labels", {})
                    if (
                        f"traefik.http.services.{role}.loadbalancer.server.port"
                        in container_labels
                    ):
                        test_passed = True
                        has_traefik_loadbalancer_label = True
                if not test_passed:
                    add_role_fail(
                        role,
                        f"traefik loadbalancer label does not exist or isn't named correctly. Should be `traefik.http.services.{role}.loadbalancer.server.port`",
                        f"roles/{role}/tasks/main.yml:{find_line_number(task_lines, 'traefik.enable')}",
                    )
                print_test_result(test_passed)

        # If hostname is set, the traefik loadbalancer label must match a port forwarded on the app
        if not has_hostname:
            print_test_skip()
        else:
            if (
                not docker_start_container_tasks
                or not has_traefik_label
                or not has_traefik_loadbalancer_label
            ):
                print_test_skip(problem=True)
            else:
                test_passed = False
                test_skipped = False
                for docker_task in docker_start_container_tasks:
                    has_network_host = (
                        docker_task["community.docker.docker_container"].get(
                            "network_mode", ""
                        )
                        == "host"
                    )
                    if has_network_host:
                        test_skipped = True
                        break  # Host mode containers don't have mapped ports, we can't check it
                    task_name = docker_task.get("name", "")
                    ports = docker_task["community.docker.docker_container"].get(
                        "ports", []
                    )
                    internal_ports = [
                        (
                            port.split(":")[1].replace("/tcp", "").replace("/udp", "")
                            if ":" in port
                            else port
                        )
                        for port in ports
                    ]
                    container_labels = docker_task[
                        "community.docker.docker_container"
                    ].get("labels", {})
                    if (
                        container_labels.get(
                            f"traefik.http.services.{role}.loadbalancer.server.port", ""
                        )
                        in internal_ports
                    ):
                        test_passed = True
                if test_skipped:
                    print_test_skip()
                else:
                    if not test_passed:
                        add_role_fail(
                            role,
                            f"`traefik.http.services.{role}.loadbalancer.server.port` label not set correctly. Should be one of the forwarded internal ports: {internal_ports}",
                            f"roles/{role}/tasks/main.yml:{find_line_number(task_lines, f'traefik.http.services.{role}.loadbalancer.server.port')}",
                        )
                    print_test_result(test_passed)

        # If hostname is set, the traefik middlewares label must be named correctly
        has_traefik_middlewares_label = False
        if not has_hostname:
            print_test_skip()
        else:
            if not docker_start_container_tasks or not has_traefik_label:
                print_test_skip(problem=True)
            else:
                test_passed = False
                for docker_task in docker_start_container_tasks:
                    task_name = docker_task.get("name", "")
                    container_labels = docker_task[
                        "community.docker.docker_container"
                    ].get("labels", {})
                    if f"traefik.http.routers.{role}.middlewares" in container_labels:
                        test_passed = True
                        has_traefik_middlewares_label = True
                if not test_passed:
                    add_role_fail(
                        role,
                        f"traefik middlewares label does not exist or isn't named correctly. Should be `traefik.http.routers.{role}.middlewares`",
                        f"roles/{role}/tasks/main.yml:{find_line_number(task_lines, 'traefik.enable')}",
                    )
                print_test_result(test_passed)

        # If hostname is set, the traefik middlewares label must be set correctly
        if not has_hostname:
            print_test_skip()
        else:
            if (
                not docker_start_container_tasks
                or not has_traefik_label
                or not has_traefik_middlewares_label
            ):
                print_test_skip(problem=True)
            else:
                test_passed = False
                for docker_task in docker_start_container_tasks:
                    task_name = docker_task.get("name", "")
                    container_labels = docker_task[
                        "community.docker.docker_container"
                    ].get("labels", {})
                    if (
                        container_labels.get(
                            f"traefik.http.routers.{role}.middlewares", ""
                        )
                        == "{{ omit if "
                        + role
                        + "_available_externally else 'blockExternal@file' }}"
                    ):
                        test_passed = True
                if not test_passed:
                    add_role_fail(
                        role,
                        f"`traefik.http.routers.{role}.middlewares` label not set correctly. Should be `{{{{ omit if {role}_available_externally else 'blockExternal@file' }}}}`",
                        f"roles/{role}/tasks/main.yml:{find_line_number(task_lines, f'traefik.http.routers.{role}.middlewares')}",
                    )
                print_test_result(test_passed)

        # All directory variables must be created
        if not directory_names:
            print_test_skip()
        else:
            test_passed = True
            for directory_var in directory_names:
                directory_var_as_var = f"{{{{ {directory_var} }}}}"
                directory_creation_task_found = False
                for task in first_block:
                    task_file = task.get("ansible.builtin.file", {})
                    if (
                        "ansible.builtin.file" in task
                        and task_file.get("state", "") == "directory"
                    ):
                        if task_file.get("path", "") == directory_var_as_var or any(
                            item.startswith(directory_var_as_var)
                            for item in task.get("with_items", [])
                        ):
                            directory_creation_task_found = True
                            break
                if not directory_creation_task_found:
                    add_role_fail(
                        role,
                        f"Directory variable `{directory_var}` is not created in task",
                        f"roles/{role}/defaults/main.yml:{find_line_number(defaults_lines, directory_var)}",
                    )
                    test_passed = False
            print_test_result(test_passed)

        # All docker containers listed in container_names_list must be created
        if not container_names_list_is_list:
            print_test_skip()
        else:
            if not docker_start_container_tasks:
                print_test_skip(problem=True)
            else:
                test_passed = True
                created_containers = set()
                for docker_task in docker_start_container_tasks:
                    container_name = docker_task[
                        "community.docker.docker_container"
                    ].get("name", "")
                    created_containers.add(container_name)
                if container_name not in created_containers:
                    container_var_name = container_name.replace("{{ ", "").replace(
                        " }}", ""
                    )
                    container_actual_name = defaults_yaml.get(
                        container_var_name, container_var_name
                    )
                    add_role_fail(
                        role,
                        f"Docker container `{container_name}` ({container_actual_name}) listed in `{role}_container_names` but no matching docker container created in tasks",
                        f"roles/{role}/defaults/main.yml:{find_line_number(defaults_lines, container_name)}",
                    )
                    test_passed = False
                print_test_result(test_passed)

        # All created containers must get removed
        if not container_names_list_is_list:
            print_test_skip()
        else:
            if not docker_start_container_tasks:
                print_test_skip(problem=True)
            else:
                test_passed = True
                created_containers = set()
                for docker_task in docker_start_container_tasks:
                    container_name = docker_task[
                        "community.docker.docker_container"
                    ].get("name", "")
                    created_containers.add(container_name)
                for docker_task in docker_stop_container_tasks:
                    container_name = docker_task[
                        "community.docker.docker_container"
                    ].get("name", "")
                    if container_name in created_containers:
                        created_containers.remove(container_name)
                if created_containers:
                    container_var_names = [
                        name.replace("{{ ", "").replace(" }}", "")
                        for name in created_containers
                    ]
                    container_actual_names = [
                        defaults_yaml.get(var_name, var_name)
                        for var_name in container_var_names
                    ]
                    add_role_fail(
                        role,
                        f"Not all containers created are removed in stop tasks. Remaining: {created_containers} ({container_actual_names})",
                        f"roles/{role}/tasks/main.yml:{find_line_number(task_lines, created_containers.pop())}",
                    )
                    test_passed = False
                print_test_result(test_passed)

        # Only created containers should get removed
        if not container_names_list_is_list:
            print_test_skip()
        else:
            if not docker_start_container_tasks:
                print_test_skip(problem=True)
            else:
                test_passed = True
                removed_containers = set()
                for docker_task in docker_stop_container_tasks:
                    container_name = docker_task[
                        "community.docker.docker_container"
                    ].get("name", "")
                    removed_containers.add(container_name)
                for docker_task in docker_start_container_tasks:
                    container_name = docker_task[
                        "community.docker.docker_container"
                    ].get("name", "")
                    if container_name in removed_containers:
                        removed_containers.remove(container_name)
                if removed_containers:
                    container_var_names = [
                        name.replace("{{ ", "").replace(" }}", "")
                        for name in removed_containers
                    ]
                    container_actual_names = [
                        defaults_yaml.get(var_name, var_name)
                        for var_name in container_var_names
                    ]
                    add_role_fail(
                        role,
                        f"Some containers are removed that aren't created by this role: {removed_containers} ({container_actual_names})",
                        f"roles/{role}/tasks/main.yml:{find_line_number(task_lines, removed_containers.pop())}",
                    )
                    test_passed = False
                print_test_result(test_passed)

        # Any created networks must be removed
        docker_start_network_tasks = [
            task for task in first_block if "community.docker.docker_network" in task
        ]
        docker_stop_network_tasks = [
            task for task in second_block if "community.docker.docker_network" in task
        ]
        if not docker_start_network_tasks:
            print_test_skip()
        else:
            test_passed = True
            created_networks = set()
            for docker_task in docker_start_network_tasks:
                network_name = docker_task["community.docker.docker_network"].get(
                    "name", ""
                )
                created_networks.add(network_name)
            for docker_task in docker_stop_network_tasks:
                network_name = docker_task["community.docker.docker_network"].get(
                    "name", ""
                )
                if network_name in created_networks:
                    created_networks.remove(network_name)
            if created_networks:
                network_var_names = [
                    name.replace("{{ ", "").replace(" }}", "")
                    for name in created_networks
                ]
                network_actual_names = [
                    defaults_yaml.get(var_name, var_name)
                    for var_name in network_var_names
                ]
                add_role_fail(
                    role,
                    f"Not all networks created are removed in stop tasks. Remaining: {created_networks} ({network_actual_names})",
                    f"roles/{role}/tasks/main.yml:{find_line_number(task_lines, created_networks.pop())}",
                )
                test_passed = False
            print_test_result(test_passed)


#
# Tests across roles
#
print()
print()
print("Running tests across roles...")

# Check for port conflicts
port_check_passed = True
port_check_host_mode_conflict = False
print()
print("Checking for port conflicts across roles...")
reversed_ports_in_use = dict()
reversed_ports_in_use_udp = dict()
for key, value in ports_in_use.items():
    if "_udp_" not in key:
        if value not in reversed_ports_in_use:
            reversed_ports_in_use[value] = [key]
        else:
            reversed_ports_in_use[value].append(key)
    else:
        if value not in reversed_ports_in_use_udp:
            reversed_ports_in_use_udp[value] = [key]
        else:
            reversed_ports_in_use_udp[value].append(key)
for port, keys in reversed_ports_in_use.items():
    if len(keys) > 1:
        print(ERROR_TAG + f"Port conflict detected on port {port} used by: {keys}")
        cross_role_fail_count += 1
        port_check_passed = False
        if any("(host mode)" in key for key in keys):
            port_check_host_mode_conflict = True
for port, keys in reversed_ports_in_use_udp.items():
    if len(keys) > 1:
        print(ERROR_TAG + f"UDP Port conflict detected on port {port} used by: {keys}")
        cross_role_fail_count += 1
        port_check_passed = False

if port_check_passed:
    print(PASS_TAG + "No port conflicts detected.")
else:
    print()
    print(
        INFO_TAG
        + "If a port conflict is detected with a UDP port, make sure to include `_udp_` in the variable name to differentiate from TCP ports."
    )
    if port_check_host_mode_conflict:
        print(
            INFO_TAG
            + "If a port conflict occurs with an application marked `(host mode)`, it likely cannot change it's port. You might need to move the other conflicting application to a different port."
        )

# Check for hostname conflicts
hostname_check_passed = True
print()
print("Checking for hostname conflicts across roles...")
reversed_hostnames_in_use = dict()
for key, value in hostnames_in_use.items():
    if value not in reversed_hostnames_in_use:
        reversed_hostnames_in_use[value] = [key]
    else:
        reversed_hostnames_in_use[value].append(key)
for hostname, keys in reversed_hostnames_in_use.items():
    if len(keys) > 1:
        print(
            ERROR_TAG
            + f"Hostname conflict detected on hostname {hostname} used by: {keys}"
        )
        cross_role_fail_count += 1
        hostname_check_passed = False

if hostname_check_passed:
    print(PASS_TAG + "No hostname conflicts detected.")

#
# Summary
#
fail_count = cross_role_fail_count + sum(len(fails) for fails in role_fails.values())
role_fail_count_total = sum(len(fails) for fails in role_fails.values())
print()
print("============")
print("Test Summary")
print("============")
print("Total Failures:".ljust(22), end="")
if fail_count == 0:
    print_color(bcolors.OKGREEN, f"{fail_count}")
else:
    print_color(bcolors.FAIL, f"{fail_count}")

print(" Fails in Roles:".ljust(22), end="")
if role_fail_count_total == 0:
    print_color(bcolors.OKGREEN, f"{role_fail_count_total}")
else:
    print_color(bcolors.FAIL, f"{role_fail_count_total}")

print(" Fails across Roles:".ljust(22), end="")
if cross_role_fail_count == 0:
    print_color(bcolors.OKGREEN, f"{cross_role_fail_count}")
else:
    print_color(bcolors.FAIL, f"{cross_role_fail_count}")


if role_fail_count_total > 0:
    longest_role_name_length = max(len(role) for role in role_fails.keys())
    longest_failure_name_length = max(
        len(fail[0]) for fails in role_fails.values() for fail in fails
    )
    print()
    print("Failures by Role:")
    print()
    for role, fails in role_fails.items():
        print(f" {role.ljust(longest_role_name_length+2)}", end="")
        print_color(bcolors.FAIL, f"{len(fails)}")
        for fail in fails:
            print(f"   - ", end="")
            print_color(
                bcolors.FAIL,
                f"{fail[0]} ",
                newline=False,
            )
            print_color([bcolors.GREY, bcolors.UNDERLINE], fail[1])


if fail_count > 0:
    sys.exit(1)
