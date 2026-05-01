This is a special folder

All contents in this folder are gitignored (except this README file), are ignored by ansible-lint, and ignored by tests.
This folder is intended to hold personal roles that are not meant to be shared with others for whatever reason.
This could be because they are private applications, or because they are experimental and not ready for sharing yet.

When adding a personal application, make sure to update the `personal_playbook.yml` file in the root of the repository, and run `git update-index --skip-worktree personal_playbook.yml` to tell git not to track changes to keep a clean environment.

You can use `git update-index --no-skip-worktree personal_playbook.yml` to undo this.

Remember if you have created a role that you think would be useful to others, consider sharing it with the community and creating a pull request! Contributions are always welcome.
