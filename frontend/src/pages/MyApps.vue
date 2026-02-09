<template>
	<div class="flex min-h-screen bg-black text-white font-sans">
		<aside class="w-64 border-r border-gray-800 flex flex-col p-6">
			<div class="flex items-center gap-3 mb-10 px-2">
				<div class="w-8 h-8 rounded bg-white flex items-center justify-center">
					<div class="w-4 h-4 bg-black rounded-sm"></div>
				</div>
				<span class="font-bold text-xl tracking-tight">Marketplace</span>
			</div>

			<nav class="space-y-1">
				<router-link
					to="/my-apps"
					class="flex items-center px-3 py-2 rounded-lg bg-white/5 text-white font-medium"
				>
					My Apps
				</router-link>
				<router-link
					to="/profile"
					class="flex items-center px-3 py-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
				>
					Profile
				</router-link>
			</nav>
		</aside>

		<main class="flex-1 flex flex-col">
			<header class="h-16 border-b border-gray-800 flex items-center justify-between px-8">
				<h1 class="text-sm font-medium text-gray-400 uppercase tracking-widest">
					My Apps
				</h1>
				<Button
					v-if="appsResource.data?.length"
					variant="subtle"
					size="sm"
					@click="goToCreateApp"
				>
					+ New App
				</Button>
			</header>

			<section class="flex-1 p-8">
				<div
					v-if="appsResource.data && appsResource.data.length > 0"
					class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
				>
					<div
						v-for="app in appsResource.data"
						:key="app.name"
						class="p-6 bg-[#111111] border border-gray-800 rounded-2xl hover:border-gray-600 transition-colors"
					>
						<h3 class="text-xl font-bold mb-2">{{ app.app }}</h3>
						<span
							class="text-xs px-2 py-1 bg-blue-900/30 text-blue-400 rounded-md uppercase font-medium"
						>
							{{ app.status }}
						</span>
						<div class="mt-4 flex justify-end">
							<router-link
								:to="`/app/${app.name}`"
								class="text-sm text-gray-400 hover:text-white"
							>
								Manage →
							</router-link>
						</div>
					</div>
				</div>

				<div
					v-else-if="!appsResource.loading"
					class="h-full flex items-center justify-center"
				>
					<div
						class="w-full max-w-2xl border border-dashed border-gray-800 rounded-3xl p-20 flex flex-col items-center"
					>
						<p class="text-gray-500 mb-8 text-lg font-medium">No apps listed yet</p>
						<Button
							variant="solid"
							class="px-8 py-6 rounded-xl font-semibold shadow-lg"
							@click="goToCreateApp"
						>
							Create your first app
						</Button>
					</div>
				</div>

				<div v-else class="h-full flex items-center justify-center">
					<div class="animate-spin rounded-full h-8 w-8 border-t-2 border-white"></div>
				</div>
			</section>
		</main>
	</div>
</template>

<script setup>
import { createListResource, Button } from "frappe-ui";
import { useRouter } from "vue-router";
import { session } from "@/data/session";

const router = useRouter();

const appsResource = createListResource({
	doctype: "Marketplace App",
	fields: ["name", "app", "status"],
	filters: {
		owner: session.user,
	},
	auto: true,
});

function goToCreateApp() {
	router.push("/create-app");
}
</script>

<style scoped>
.router-link-active {
	@apply bg-white/10 text-white;
}
</style>
