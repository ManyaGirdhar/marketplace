<template>
	<div>
		<div
			v-if="appsResource.data && appsResource.data.length > 0"
			class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
		>
			<div
				v-for="app in appsResource.data"
				:key="app.name"
				class="p-6 bg-white border rounded-xl hover:shadow-md transition"
			>
				<h3 class="text-xl font-semibold mb-2">{{ app.app }}</h3>

				<span class="text-xs px-2 py-1 bg-blue-50 text-blue-600 rounded">
					{{ app.status }}
				</span>

				<div class="mt-4 flex justify-end">
					<router-link
						:to="{ name: 'AppDetails', params: { app_name: app.app } }"
						class="text-sm text-blue-600 hover:underline"
					>
						Manage →
					</router-link>
				</div>
			</div>
		</div>

		<div
			v-else-if="!appsResource.loading"
			class="h-[60vh] flex flex-col items-center justify-center gap-6"
		>
			<p class="text-gray-500 text-lg">No apps listed yet</p>

			<Button @click="goToCreateApp">Create your first app</Button>
		</div>

		<div v-else class="h-[60vh] flex items-center justify-center">
			<LoadingIndicator class="w-8 h-8" />
		</div>
	</div>
</template>

<script setup>
import { createListResource, Button, LoadingIndicator } from "frappe-ui";
import { useRouter } from "vue-router";
import { session } from "@/data/session";

const router = useRouter();

const appsResource = createListResource({
	doctype: "Marketplace App",
	fields: ["name", "app", "status"],
	filters: { owner: session.user },
	auto: true,
});

function goToCreateApp() {
	router.push({ name: "CreateApp" });
}
</script>
