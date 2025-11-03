import os
import subprocess
import sys
import fileinput
import re

if len(sys.argv) != 2:
    print("Usage: python breaking_changes.py <application_name>")
    sys.exit(1)

# Change working directory to the script's directory
dirname = os.path.dirname(os.path.realpath(__file__))
os.chdir(dirname)

application_to_check = sys.argv[1]
current_git_commit_hash = (
    subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()
)

# Check if we're already marked as having a breaking change
breaking_change_file_path = f"../../../state/BREAKING_CHANGE_{application_to_check}.txt"
if os.path.exists(breaking_change_file_path):
    sys.exit(1)

# Open state file
state_file_path = "../../../state/application_last_run_hashes.csv"
if not os.path.exists(state_file_path):
    # Create the state file if it doesn't exist
    with open(state_file_path, "w") as f:
        pass

for line in fileinput.input(state_file_path, inplace=True):
    app, last_hash = line.strip().split(",")
    if app == application_to_check:
        if last_hash != current_git_commit_hash:
            commit_messages_since_last_run = ""
            try:
                commit_messages_since_last_run = (
                    subprocess.check_output(
                        [
                            "git",
                            "log",
                            "--pretty=format:%s %H",  # Commit message and hash
                            f"{last_hash}..{current_git_commit_hash}",
                        ]
                    )
                    .decode("ascii")
                    .strip()
                )
            except:
                # If git log fails (e.g., last_hash not found), assume the user knows what they're doing
                commit_messages_since_last_run = ""

            # Regardless of whether a breaking change was found, update the state to latest commit hash
            print(f"{application_to_check},{current_git_commit_hash}")

            # Check for breaking change pattern in commit messages
            breaking_change_regex = (
                r"^([a-z]+\("
                + re.escape(application_to_check)
                + r"\)!:.+) ([a-z0-9]{40})$"
            )
            regex_search = re.findall(
                breaking_change_regex,
                commit_messages_since_last_run,
                re.IGNORECASE | re.MULTILINE,
            )
            if regex_search:
                # Create a new file to mark the breaking change
                with open(breaking_change_file_path, "w") as f:
                    f.write("Breaking changes detected:\n\n")
                    f.writelines(
                        f"{msg} | https://github.com/Dylancyclone/ansible-homelab-orchestration/commit/{commit_hash}\n"
                        for msg, commit_hash in regex_search
                    )
                    f.write("\nPlease review the documentation for this application:\n")
                    f.write(
                        f"https://dylancyclone.github.io/ansible-homelab-orchestration/applications/{application_to_check}"
                    )
                    f.write(
                        "\n\nDelete this file once the breaking changes have been resolved.\n"
                    )
                sys.exit(1)
            # If no breaking change was found, just exit with success
            sys.exit(0)
        else:
            print(line.strip())
            sys.exit(0)
    else:
        print(line.strip())

# If application not found in state file, add it
with open(state_file_path, "a") as f:
    f.write(f"{application_to_check},{current_git_commit_hash}\n")
sys.exit(0)
