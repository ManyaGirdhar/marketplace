<template>
	<div>
		<div v-if="appsResource.loading" class="h-[60vh] flex items-center justify-center">
			<LoadingIndicator class="w-8 h-8" />
		</div>

		<div
			v-else-if="appsResource.data && appsResource.data.length"
			class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
		>
			<Card
				v-for="app in appsResource.data"
				:key="app.name"
				class="cursor-pointer hover:shadow-md transition p-5"
				@click="goToApp(app.app)"
			>
				<div class="flex flex-col gap-4">
					<div class="flex items-start justify-between">
						<h3 class="text-lg font-semibold truncate">
							{{ app.app }}
						</h3>

						<Badge :theme="getStatusTheme(app.status)">
							{{ app.status }}
						</Badge>
					</div>

					<div class="flex justify-end">
						<span class="text-sm text-blue-600 hover:underline"> Manage → </span>
					</div>
				</div>
			</Card>
		</div>

		<div v-else class="h-[65vh] flex items-center justify-center">
			<Card class="max-w-md text-center">
				<template #content>
					<div class="py-6 flex flex-col items-center gap-4">
						<div class="text-4xl">📦</div>

						<div>
							<h2 class="text-lg font-semibold">No apps yet</h2>
							<p class="text-sm text-gray-500 mt-1">
								Create your first Marketplace app to get started.
							</p>
						</div>

						<Button @click="goToCreateApp"> Create App </Button>
					</div>
				</template>
			</Card>
		</div>
	</div>
</template>

<script setup>
import { createListResource, Button, LoadingIndicator, Card, Badge } from "frappe-ui";
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

function goToApp(appName) {
	router.push({ name: "AppDetails", params: { app_name: appName } });
}

function getStatusTheme(status) {
	const map = {
		Draft: "gray",
		Published: "green",
		"In Review": "blue",
		"Attention Required": "orange",
		Rejected: "red",
		Disabled: "gray",
	};

	return map[status] || "gray";
}
</script>
