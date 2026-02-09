<template>
	<div class="flex min-h-screen bg-black text-white">
		<aside class="w-64 border-r border-gray-800 flex flex-col p-6">
			<div class="flex items-center gap-3 mb-10 px-2">
				<div class="w-8 h-8 rounded bg-white flex items-center justify-center">
					<div class="w-4 h-4 bg-black rounded-sm"></div>
				</div>
				<span class="font-bold text-xl">Marketplace</span>
			</div>
			<nav class="space-y-1">
				<router-link
					to="/my-apps"
					class="flex items-center px-3 py-2 rounded-lg text-gray-400 hover:text-white"
					>My Apps</router-link
				>
				<router-link
					to="/profile"
					class="flex items-center px-3 py-2 rounded-lg text-gray-400 hover:text-white"
					>Profile</router-link
				>
			</nav>
		</aside>

		<main class="flex-1 flex flex-col">
			<header class="h-16 border-b border-gray-800 flex items-center px-8">
				<h1 class="text-sm font-medium text-gray-400 uppercase tracking-widest">
					Create New App
				</h1>
			</header>

			<div class="p-8 max-w-4xl w-full mx-auto">
				<div class="mb-8">
					<h2 class="text-2xl font-semibold">Select a Repository</h2>
					<p class="text-gray-400">
						Choose the GitHub repository you want to list on the marketplace.
					</p>
				</div>

				<div v-if="reposResource.loading" class="flex justify-center py-20">
					<div class="animate-spin rounded-full h-8 w-8 border-t-2 border-white"></div>
				</div>

				<div v-else class="grid gap-4">
					<div
						v-for="repo in reposResource.data"
						:key="repo.id"
						@click="handleSelectRepo(repo)"
						class="group p-5 bg-[#111111] border border-gray-800 rounded-2xl hover:border-white/30 transition-all cursor-pointer flex items-center justify-between"
					>
						<div>
							<h3
								class="font-medium text-lg group-hover:text-blue-400 transition-colors"
							>
								{{ repo.name }}
							</h3>
							<p class="text-gray-500 text-sm truncate max-w-md">
								{{ repo.description || "No description provided." }}
							</p>
						</div>
						<div class="flex items-center gap-4 text-gray-400 text-sm">
							<span>⭐ {{ repo.stargazers_count }}</span>
							<span
								class="px-3 py-1 bg-gray-900 rounded-full border border-gray-800"
								>{{ repo.language }}</span
							>
						</div>
					</div>
				</div>
			</div>
		</main>
	</div>
</template>

<script setup>
import { createResource, call } from "frappe-ui";
import { useRouter } from "vue-router";
const router = useRouter();

const reposResource = createResource({
	url: "marketplace.api.github.get_publisher_repos",
	auto: true,
});

async function handleSelectRepo(repo) {
	router.push({
		path: "/app/new",
		query: {
			repo_url: repo.html_url,
			repo_name: repo.name,
			repo_description: repo.description || "",
		},
	});
}
</script>
