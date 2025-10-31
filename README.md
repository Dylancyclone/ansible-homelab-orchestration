# Ansible Homelab Orchestration

[![Number of Available Applications](https://img.shields.io/github/directory-file-count/Dylancyclone/ansible-homelab-orchestration/roles?label=Available%20Applications)](https://dylancyclone.github.io/ansible-homelab-orchestration/applications)
[![ansible-lint](https://github.com/Dylancyclone/ansible-homelab-orchestration/workflows/ansible-lint/badge.svg)](https://github.com/Dylancyclone/ansible-homelab-orchestration/actions?query=workflow%3Aansible-lint)
[![Tests](https://github.com/Dylancyclone/ansible-homelab-orchestration/workflows/run-tests/badge.svg)](https://github.com/Dylancyclone/ansible-homelab-orchestration/actions?query=workflow%3Arun-tests)

[Documentation](https://dylancyclone.github.io/ansible-homelab-orchestration/)

Ansible Homelab Orchestration is a project that sets up and installs applications on your homelab using Docker.

It can also leverage [Traefik](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/traefik) to provide automatic SSL certificates and reverse proxying for [external access](https://dylancyclone.github.io/ansible-homelab-orchestration/guides/dns-access/) to any/all of your applications.

## Available Applications

Ansible Homelab Orchestration currently supports [![Number of Available Applications](https://img.shields.io/github/directory-file-count/Dylancyclone/ansible-homelab-orchestration/roles?label=)](https://dylancyclone.github.io/ansible-homelab-orchestration/applications) applications! Most of which can be enabled with a single configuration line:

```yaml
<application_name>_enabled: true
```

For example:

```yaml
portainer_enabled: true
```

Some of the highlighted applications include:

- [Portainer](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/portainer) - A lightweight management UI that allows you to easily manage your Docker environments.
- [Traefik](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/traefik) - A modern reverse proxy that automatically configures SSL certificates for [external access](https://dylancyclone.github.io/ansible-homelab-orchestration/guides/dns-access/).
- [Immich](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/immich) - A self-hosted photo and video management application.
- [Jellyfin](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/jellyfin), [Plex](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/plex), and [Emby](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/emby) - Media server applications to organize, manage, and stream your media (and supporting applications).
- [Home Assistant](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/home-assistant) - An open-source home automation platform that focuses on privacy and local control.
- [Paperless-ngx](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/paperless-ngx) - A document management system that allows you to digitize and organize your paper documents.
- [RomM](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/romm) - A self-hosted solution for managing and streaming your ROM collection.
- [Syncthing](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/syncthing) - A continuous file synchronization program that synchronizes files between two or more devices in real time.
- [Drone CI](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/drone-ci) or [Woodpecker CI](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/woodpecker-ci) hooked up automatically with [Gitea](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/gitea) for self-hosted Git repositories and continuous integration.
- Complete monitoring with [Grafana](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/grafana), [Prometheus](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/prometheus), [Loki](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/loki), [Telegraf](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/telegraf), [Alloy](https://dylancyclone.github.io/ansible-homelab-orchestration/applications/alloy)

...As well as a number of choices for [dashboards](https://dylancyclone.github.io/ansible-homelab-orchestration/tags/Dashboard), [backups](https://dylancyclone.github.io/ansible-homelab-orchestration/tags/Backup), [self-hosted media](http://localhost:4321/ansible-homelab-orchestration/tags/Media%20Server), [Knowledge bases](http://localhost:4321/ansible-homelab-orchestration/tags/Knowledge%20Management), [RSS](http://localhost:4321/ansible-homelab-orchestration/tags/RSS), [budget tracking](http://localhost:4321/ansible-homelab-orchestration/tags/Finance), and more! A massive collection of applications to own your data and empower your homelab.

For a full list of all [![Number of Available Applications](https://img.shields.io/github/directory-file-count/Dylancyclone/ansible-homelab-orchestration/roles?label=)](https://dylancyclone.github.io/ansible-homelab-orchestration/applications) supported applications, please visit the [Applications](https://dylancyclone.github.io/ansible-homelab-orchestration/applications) page in the documentation!

## Getting Started

Please refer to the [Getting Started Guide](https://dylancyclone.github.io/ansible-homelab-orchestration/guides/getting-started/) in the documentation.

## Documentation

Please refer to the [Documentation](https://dylancyclone.github.io/ansible-homelab-orchestration/) for full setup instructions, configuration options, and application details.

## Contributing

Contributions are always welcome! Please refer to the [Contributing Guide](https://dylancyclone.github.io/ansible-homelab-orchestration/contributing/) for details on how to contribute to this project.
