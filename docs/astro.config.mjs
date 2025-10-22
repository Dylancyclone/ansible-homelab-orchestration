// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://dylancyclone.github.io',
  base: '/ansible-homelab-orchestration',
	integrations: [
		starlight({
			title: 'Ansible Homelab Orchestration',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/Dylancyclone/ansible-homelab-orchestration' }],
			customCss: ["./src/styles/main.css"],
			sidebar: [
				{
					label: 'Guides',
					autogenerate: { directory: 'guides' },
				},
				// {
				// 	label: 'Applications',
				// 	link: '/applications/example',
				// },
				{
					label: 'Applications List',
					autogenerate: { directory: 'applications' },
				},
			],
		}),
	],
});
