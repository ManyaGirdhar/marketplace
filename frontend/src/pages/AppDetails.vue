<template>
	<div class="p-6 max-w-5xl mx-auto">
		<div v-if="loading">Loading app...</div>

		<div v-else-if="app">
			<Card>
				<div class="flex items-center justify-between">
					<div>
						<h1 class="text-3xl font-semibold">{{ app.app }}</h1>
						<p class="text-gray-500 mt-1">{{ app.tagline }}</p>
					</div>

					<Badge>{{ app.category || "Uncategorized" }}</Badge>
				</div>
			</Card>
			<Card title="Overview" class="mt-6">
				<p class="whitespace-pre-line">{{ app.description }}</p>
			</Card>
			<Card title="Details" class="mt-6">
				<div class="grid grid-cols-2 gap-4">
					<div>
						<p class="text-sm text-gray-500">Publisher</p>
						<p class="font-medium">{{ app.publisher }}</p>
					</div>

					<div>
						<p class="text-sm text-gray-500">License</p>
						<p>{{ app.license }}</p>
					</div>

					<div>
						<p class="text-sm text-gray-500">Repository</p>
						<a :href="app.url" target="_blank" class="text-blue-600"> View Repo </a>
					</div>

					<div>
						<p class="text-sm text-gray-500">Status</p>
						<Badge>{{ app.status }}</Badge>
					</div>
				</div>
			</Card>
		</div>

		<div v-else class="text-red-500">App not found</div>
	</div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { createResource } from "frappe-ui";

const route = useRoute();
const app = ref(null);
const loading = ref(true);

const appResource = createResource({
	url: "frappe.client.get",
	params: {
		doctype: "Marketplace App",
		filters: { app: route.params.app },
	},
	auto: false,
});

onMounted(async () => {
	try {
		const res = await appResource.fetch();
		app.value = res;
	} catch (err) {
		console.error(err);
	} finally {
		loading.value = false;
	}
});
</script>
