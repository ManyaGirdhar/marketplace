import { userResource } from "@/data/user";
import { createRouter, createWebHistory } from "vue-router";
import { session } from "./data/session";
import { call } from "frappe-ui";

const routes = [
	{ path: "/", name: "Home", component: () => import("@/pages/Home.vue") },
	{ name: "Login", path: "/account/login", component: () => import("@/pages/Login.vue") },
	{
		name: "PublisherSetup",
		path: "/publishersetup",
		component: () => import("@/pages/PublisherSetup.vue"),
	},
	{ name: "MyApps", path: "/my-apps", component: () => import("@/pages/MyApps.vue") },
	{ name: "CreateApp", path: "/create-app", component: () => import("@/pages/CreateApp.vue") },
	{ name: "ManageApp", path: "/app/:appName", component: () => import("@/pages/ManageApp.vue") },
];

const router = createRouter({
	history: createWebHistory("/dashboard"),
	routes,
});

export const publisherState = {
	checked: false,
	hasProfile: false,
};

router.beforeEach(async (to, from, next) => {
	// 1. Safe wait for user data
	if (userResource?.promise) {
		await userResource.promise.catch(() => {});
	}

	const isLoggedIn = session.isLoggedIn;

	// 2. Auth Gate
	if (!isLoggedIn) {
		if (to.name === "Login") {
			return next();
		}
		return next({ name: "Login" });
	}

	// 3. Logic for Logged-in Users
	if (isLoggedIn) {
		// Check Publisher Status if not already known
		if (!publisherState.checked && session.user) {
			try {
				const response = await call("frappe.client.get_value", {
					doctype: "Marketplace Publisher",
					filters: { user: session.user },
					fieldname: "name",
				});

				publisherState.hasProfile = !!(response && response.name);
				publisherState.checked = true;
			} catch (e) {
				publisherState.hasProfile = false;
				publisherState.checked = true;
			}
		}

		// Redirect Logic
		if (!publisherState.hasProfile) {
			if (to.name !== "PublisherSetup") {
				return next({ name: "PublisherSetup" });
			}
		} else {
			const restrictedForPublishers = ["Login", "Home", "PublisherSetup"];
			if (restrictedForPublishers.includes(to.name)) {
				return next({ name: "MyApps" });
			}
		}
	}

	next();
});

export default router;
