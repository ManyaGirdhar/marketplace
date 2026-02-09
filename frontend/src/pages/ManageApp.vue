<template>
	<div class="flex h-screen bg-black text-white font-sans overflow-hidden">
		<Sidebar
			:header="sidebarConfig.header"
			:sections="sidebarConfig.sections"
			class="border-r border-gray-800"
		/>

		<div class="flex-1 flex flex-col min-w-0 overflow-hidden">
			<header
				class="flex items-center justify-between px-8 py-5 border-b border-gray-800 bg-black/60 backdrop-blur-md sticky top-0 z-20"
			>
				<div class="space-y-1">
					<p class="text-xs uppercase tracking-widest text-gray-500">Submit App</p>

					<div class="flex items-center gap-4">
						<h1 class="text-lg font-semibold text-white truncate max-w-[420px]">
							{{ form.app_title || "New App" }}
						</h1>

						<!-- Progress Dots -->
						<div class="flex items-center gap-2">
							<div
								v-for="step in 3"
								:key="step"
								:class="[
									'h-2 rounded-full transition-all duration-300',
									currentStep >= step
										? 'w-6 bg-white shadow-[0_0_10px_rgba(255,255,255,0.6)]'
										: 'w-2 bg-gray-700',
								]"
							/>
						</div>
					</div>
				</div>

				<Button
					variant="solid"
					:loading="processing"
					:disabled="isNextDisabled"
					@click="handleContinue"
					class="min-w-[120px]"
				>
					{{ currentStep === 3 ? "Finish" : "Continue" }}
				</Button>
			</header>

			<main class="flex-1 overflow-y-auto bg-[#050505]">
				<div class="max-w-5xl mx-auto px-8 py-10">
					<div class="mb-10 flex items-center justify-between">
						<div class="flex gap-8">
							<div
								v-for="(label, index) in ['App Details', 'Validation', 'Review']"
								:key="label"
								class="flex items-center gap-3"
							>
								<div
									:class="[
										'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
										currentStep > index + 1
											? 'bg-white text-black'
											: currentStep === index + 1
											? 'border border-white text-white'
											: 'border border-gray-700 text-gray-600',
									]"
								>
									{{ index + 1 }}
								</div>
								<span
									:class="[
										'text-sm',
										currentStep === index + 1 ? 'text-white' : 'text-gray-500',
									]"
								>
									{{ label }}
								</span>
							</div>
						</div>
					</div>

					<div class="bg-[#0A0A0A] border border-gray-800 rounded-3xl p-8">
						<Step1Details
							v-if="currentStep === 1"
							:form="form"
							:branches="repoMeta.branches"
							:dependencies="repoMeta.dependencies"
							:loadingMeta="repoMeta.loading"
						/>

						<Step2Validation
							v-if="currentStep === 2"
							:form="form"
							@validated="handleValidationUpdate"
						/>

						<Step3Review v-if="currentStep === 3" :form="form" />
					</div>
				</div>
			</main>
		</div>
	</div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Sidebar, Button, call } from "frappe-ui";

import Step1Details from "./wizard_steps/Step1Details.vue";
import Step2Validation from "./wizard_steps/Step2Validation.vue";
import Step3Review from "./wizard_steps/Step3Review.vue";

const currentStep = ref(1);
const processing = ref(false);
const validationPassed = ref(false);

const route = useRoute();
const router = useRouter();

const form = reactive({
	app_name: route.query.repo_name || "",
	app_title: route.query.repo_name || "",
	repo_url: route.query.repo_url || "",
	description: route.query.repo_description || "",
	branch: "",
	logo: null,
	app_release_id: "",
	versions: [{ version: "", branch: "" }],
});

const repoMeta = reactive({
	branches: [],
	dependencies: [],
	loading: false,
});

const repoData = ref({});

onMounted(async () => {
	if (!form.repo_url) {
		router.replace("/new-app");
		return;
	}

	repoMeta.loading = true;

	try {
		const data = await call("marketplace.api.github.fetch_repo_info", {
			repo_url: form.repo_url,
		});

		repoData.value = data.raw_github_data || {};

		if (data.metadata) {
			form.app_name = data.metadata.app_name || form.app_name;
			form.app_title = data.metadata.app_title || form.app_title;
			form.description = data.metadata.app_description || form.description;
		}

		if (data.default_branch) {
			form.versions[0].branch = data.default_branch;
		}

		repoMeta.branches = data.branches || [];
		repoMeta.dependencies = data.metadata?.dependencies || [];
	} catch (err) {
		console.error("Repo bootstrap failed", err);
	} finally {
		repoMeta.loading = false;
	}
});

const isNextDisabled = computed(() => {
	if (currentStep.value === 1) {
		return !form.app_name || !form.repo_url || processing.value;
	}
	if (currentStep.value === 2) {
		return !validationPassed.value || processing.value;
	}
	return processing.value;
});

const sidebarConfig = reactive({
	header: {
		title: "Marketplace",
		subtitle: "Publisher Portal",
		logo: "",
		menuItems: [
			{ label: "Settings", icon: "settings", onClick: () => {} },
			{ label: "Logout", icon: "log-out", onClick: () => {} },
		],
	},
	sections: [
		{
			items: [
				{ label: "My Apps", to: "/my-apps", active: true },
				{ label: "Notifications", to: "/notifications" },
			],
		},
		{
			items: [{ label: "Build Logs", to: "/logs" }],
		},
	],
});

async function handleContinue() {
	if (currentStep.value === 1) {
		const success = await initializeApp();
		if (success) currentStep.value = 2;
		return;
	}

	if (currentStep.value === 2) {
		if (validationPassed.value) {
			currentStep.value = 3;
		}
		return;
	}

	if (currentStep.value === 3) {
		processing.value = true;
		try {
			await call("marketplace.api.setup_wizard.finalize_submission", {
				app_release_id: form.app_release_id,
			});
			router.push("/my-apps");
		} catch (error) {
			console.error("Finalization failed:", error);
		} finally {
			processing.value = false;
		}
	}
}

async function initializeApp() {
	processing.value = true;
	try {
		const res = await call("marketplace.api.setup_wizard.initialize_app_step_1", {
			form_data: JSON.stringify(form),
			repo_data: repoData.value,
		});
		form.app_release_id = res.app_release;
		return true;
	} catch (error) {
		console.error(error);
		return false;
	} finally {
		processing.value = false;
	}
}

function handleValidationUpdate(status: boolean) {
	validationPassed.value = status;
}
</script>
