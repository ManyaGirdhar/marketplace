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
										'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
										currentStep > index + 1
											? 'bg-gray-900 text-white dark:bg-white dark:text-black'
											: currentStep === index + 1
											? 'border border-gray-900 dark:border-white'
											: 'border border-gray-300 dark:border-gray-700 text-gray-400',
									]"
								>
									{{ index + 1 }}
								</div>
								<span
									:class="[
										'text-sm',
										currentStep === index + 1 ? '' : 'text-gray-500',
									]"
								>
									{{ label }}
								</span>
							</div>
						</div>
					</div>

					<div
						class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-sm"
					>
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
import { Button, call } from "frappe-ui";

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
