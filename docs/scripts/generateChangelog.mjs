import { loadEnv } from "vite"
import { request } from "@octokit/request"
import fs from "fs"

let GH_TOKEN = ""

if (process.argv.includes("--ci")) {
	// In CI, grab GH_TOKEN from environment variables
	GH_TOKEN = process.env.GH_TOKEN || ""
} else {
	GH_TOKEN = loadEnv(process.env.NODE_ENV, process.cwd(), "").GH_TOKEN
}

if (!GH_TOKEN) {
	console.warn(
		"Warning: GH_TOKEN is not set in environment variables, skipping generating changelog."
	)
	process.exit(0)
}

const result = await request("GET /repos/{owner}/{repo}/commits", {
	headers: {
		authorization: `token ${GH_TOKEN}`,
		"X-GitHub-Api-Version": "2022-11-28",
	},
	owner: "Dylancyclone",
	repo: "ansible-homelab-orchestration",
	per_page: 100,
})

fs.writeFileSync(
	"./public/changelog.json",
	JSON.stringify(result.data, null, 2)
)
console.log("Changelog generated: changelog.json")
