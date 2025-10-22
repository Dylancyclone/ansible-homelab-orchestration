// @ts-check
import { defineConfig } from "astro/config"
import starlight from "@astrojs/starlight"
import mermaid from 'astro-mermaid';

// https://astro.build/config
export default defineConfig({
	site: "https://dylancyclone.github.io",
	base: "/ansible-homelab-orchestration",
	trailingSlash: "never",
	integrations: [
    mermaid({
      theme: 'default',
      autoTheme: true
    }),
		starlight({
			title: "Ansible Homelab Orchestration",
			social: [
				{
					icon: "github",
					label: "GitHub",
					href: "https://github.com/Dylancyclone/ansible-homelab-orchestration",
				},
			],
			customCss: ["./src/styles/main.css"],
			sidebar: [
				{
					label: "Guides",
					autogenerate: { directory: "guides" },
				},
				{
					label: 'Browse Applications',
					link: '/tags',
				},
				{
					label: "Applications List",
					autogenerate: { directory: "applications" },
				},
			],
		}),
	],
})
