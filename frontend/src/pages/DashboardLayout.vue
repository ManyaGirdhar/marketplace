<template>
	<div class="flex h-screen w-screen overflow-hidden bg-white dark:bg-gray-950">
		<Sidebar :header="sidebarConfig.header" :sections="sidebarConfig.sections" />
		<div class="flex flex-1 flex-col overflow-auto">
			<header
				class="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-5 py-3"
			>
				<Breadcrumbs :items="breadcrumbItems" />
			</header>
			<main class="flex-1 overflow-y-auto p-6 bg-gray-50 dark:bg-gray-950">
				<router-view />
			</main>
		</div>
	</div>
</template>

<script setup lang="ts">
import { reactive, computed } from "vue";
import { Sidebar, Breadcrumbs } from "frappe-ui";
import { useRoute } from "vue-router";
import { session } from "../data/session";
import { LayoutDashboard, PlusCircle, UserCircle, LogOut, Moon } from "lucide-vue-next";

const route = useRoute();

const breadcrumbItems = computed(() => {
	const items = [{ label: "App Dashboard", route: { name: "MyApps" } }];

	if (route.name === "ManageApp") {
		items.push({
			label: String(route.params.appName ?? "App"),
			route: { name: "MyApps" },
		});
	} else if (route.name === "CreateApp") {
		items.push({
			label: "Create App",
			route: { name: "CreateApp" },
		});
	} else if (route.name === "PublisherProfile") {
		items.push({
			label: "Publisher Profile",
			route: { name: "PublisherProfile" },
		});
	}

	return items;
});

function toggleTheme() {
	const currentTheme = document.documentElement.getAttribute("data-theme");
	const newTheme = currentTheme === "dark" ? "light" : "dark";
	document.documentElement.setAttribute("data-theme", newTheme);
}

const sidebarConfig = reactive({
	header: {
		title: "Marketplace",
		subtitle: session.user || "Publisher",
		logo: "",
		menuItems: [
			{
				label: "Toggle Theme",
				icon: Moon,
				onClick: toggleTheme,
			},
			{
				label: "Logout",
				icon: LogOut,
				onClick: () => session.logout(),
			},
		],
	},
	sections: [
		{
			label: "Publishing",
			items: [
				{
					label: "My Apps",
					to: "/dashboard/my-apps",
					icon: LayoutDashboard,
				},
				{
					label: "Create New App",
					to: "/dashboard/create-app",
					icon: PlusCircle,
				},
			],
		},
		{
			label: "Account",
			collapsible: true,
			items: [
				{
					label: "Publisher Profile",
					to: "/dashboard/publisher-profile",
					icon: UserCircle,
				},
			],
		},
	],
});
</script>
