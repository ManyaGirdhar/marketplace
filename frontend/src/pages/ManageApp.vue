<template>
	<div
		class="flex h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 font-sans overflow-hidden"
	>
		<div class="flex-1 flex flex-col min-w-0 overflow-hidden">
			<header
				class="flex items-center justify-between px-8 py-5 border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-950/70 backdrop-blur sticky top-0 z-20"
			>
				<div class="space-y-2">
					<p
						class="text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400"
					>
						Submit App
					</p>
					<h1
						class="text-2xl font-semibold text-gray-900 dark:text-white truncate max-w-[520px]"
					>
						{{ form.app_title || "New App" }}
					</h1>
				</div>

				<div class="flex items-center gap-4">
					<div
						v-if="isValidating"
						class="flex items-center gap-2 text-sm text-gray-500 italic"
					>
						<div
							class="w-4 h-4 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin"
						></div>
						Verifying...
					</div>
					<div
						v-else-if="validationPassed && currentStep === 1"
						class="flex items-center gap-2 text-sm text-green-600 font-medium"
					>
						<span
							class="w-5 h-5 flex items-center justify-center bg-green-500 text-white rounded-full text-[10px]"
							>✓</span
						>
						Compatible
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
				</div>
			</header>

			<main class="flex-1 overflow-y-auto">
				<div class="max-w-5xl mx-auto px-8 py-10">
					<div class="mb-10 flex items-center justify-center">
						<div class="flex gap-10">
							<div
								v-for="(label, index) in ['App Details', 'Validation', 'Review']"
								:key="label"
								class="flex items-center gap-3"
							>
								<div
									:class="[
										'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300',
										currentStep > index + 1
											? 'bg-gray-900 text-white'
											: currentStep === index + 1
											? 'border-2 border-gray-900 ring-4 ring-gray-100'
											: 'border border-gray-300 text-gray-400',
									]"
								>
									{{ index + 1 }}
								</div>
								<span
									:class="[
										'text-sm font-medium',
										currentStep === index + 1
											? 'text-gray-900'
											: 'text-gray-500',
									]"
									>{{ label }}</span
								>
							</div>
						</div>
					</div>

					<div
						class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-sm"
					>
						<div
							v-if="validationError"
							class="mb-6 p-4 bg-red-50 border border-red-100 rounded-2xl text-red-700 text-sm flex items-center gap-3 animate-pulse"
						>
							<span class="text-lg">⚠️</span>
							{{ validationError }}
						</div>

						<Step1Details
							v-if="currentStep === 1"
							:form="form"
							:branches="repoMeta.branches"
							:dependencies="repoMeta.dependencies"
							:loadingMeta="repoMeta.loading"
							:frappeRequirement="repoMeta.frappe_requirement"
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
import { reactive, ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Button, call } from "frappe-ui";

import Step1Details from "./wizard_steps/Step1Details.vue";
import Step2Validation from "./wizard_steps/Step2Validation.vue";
import Step3Review from "./wizard_steps/Step3Review.vue";

const currentStep = ref(1);
const processing = ref(false);
const isValidating = ref(false);
const validationPassed = ref(false);
const validationError = ref("");

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
	frappe_requirement: null,
});

const repoData = ref({});

watch(
	() => form.versions,
	() => {
		validationError.value = "";
		validationPassed.value = false;
	},
	{ deep: true }
);

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
			repoMeta.frappe_requirement = data.metadata.frappe_version_requirement;
		}
		if (data.default_branch) form.versions[0].branch = data.default_branch;
		repoMeta.branches = data.branches || [];
		repoMeta.dependencies = data.metadata?.dependencies || [];
	} finally {
		repoMeta.loading = false;
	}
});

async function checkCompatibility() {
	if (!repoMeta.frappe_requirement) {
		validationPassed.value = true;
		return true;
	}

	const selectedVersion = form.versions[0]?.version;
	if (!selectedVersion) {
		validationError.value = "Please select a Frappe version.";
		return false;
	}

	isValidating.value = true;
	try {
		const isCompatible = await call("marketplace.api.github.check_version_compatibility", {
			required_range: repoMeta.frappe_requirement,
			user_version: selectedVersion,
		});

		if (!isCompatible) {
			validationError.value = `This app requires Frappe ${repoMeta.frappe_requirement}. Your selection (${selectedVersion}) is incompatible.`;
			validationPassed.value = false;
			return false;
		}

		validationError.value = "";
		validationPassed.value = true;
		return true;
	} finally {
		isValidating.value = false;
	}
}

const isNextDisabled = computed(() => {
	if (currentStep.value === 1) {
		return (
			!form.app_name || !form.versions[0]?.version || processing.value || isValidating.value
		);
	}
	if (currentStep.value === 2) return !validationPassed.value || processing.value;
	return processing.value;
});

async function handleContinue() {
	if (currentStep.value === 1) {
		const compatible = await checkCompatibility();

		if (!compatible) return;

		processing.value = true;
		try {
			const success = await initializeApp();
			if (success) currentStep.value = 2;
		} finally {
			processing.value = false;
		}
		return;
	}

	if (currentStep.value === 2 && validationPassed.value) {
		currentStep.value = 3;
		return;
	}

	if (currentStep.value === 3) {
		processing.value = true;
		try {
			await call("marketplace.api.setup_wizard.finalize_submission", {
				app_release_id: form.app_release_id,
			});
			router.push("/my-apps");
		} finally {
			processing.value = false;
		}
	}
}

async function initializeApp() {
	try {
		const res = await call("marketplace.api.setup_wizard.initialize_app_step_1", {
			form_data: JSON.stringify(form),
			repo_data: repoData.value,
		});
		form.app_release_id = res.app_release;
		return true;
	} catch (error: any) {
		console.error("Initialization Error:", error);
		let errorMessage = "An error occurred while creating the app record.";

		if (error.messages && error.messages.length > 0) {
			errorMessage = error.messages[0];
		} else if (error.message) {
			errorMessage = error.message;
		}
		validationError.value = errorMessage;

		return false;
	}
}
function handleValidationUpdate(status: boolean) {
	validationPassed.value = status;
}
</script>
