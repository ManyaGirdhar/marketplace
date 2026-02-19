<template>
	<div class="space-y-10">
		<section class="space-y-6">
			<h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">App Identity</h2>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-10">
				<div class="space-y-6">
					<TextInput
						label="App Title"
						v-model="form.app_title"
						placeholder="e.g. Airplane Mode"
						description="Public name shown on Marketplace"
					/>

					<TextInput
						label="App Name"
						v-model="form.app_name"
						variant="read-only"
						description="Derived from repository (immutable)"
					/>

					<TextInput
						label="Repository URL"
						v-model="form.repo_url"
						variant="read-only"
						description="Used to fetch branches and metadata"
					/>
				</div>

				<div class="space-y-6">
					<div
						class="border border-gray-200 dark:border-gray-700 rounded-xl p-5 bg-gray-50 dark:bg-gray-800"
					>
						<div class="flex items-center gap-2 mb-3">
							<FeatherIcon
								name="layers"
								class="w-4 h-4 text-gray-500 dark:text-gray-400"
							/>
							<p class="text-sm font-medium text-gray-700 dark:text-gray-200">
								Detected Dependencies
							</p>
						</div>
						<div
							v-if="frappeRequirement"
							class="mt-4 flex items-start gap-2 text-xs bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 p-3 rounded-lg border border-blue-100 dark:border-blue-800"
						>
							<FeatherIcon name="info" class="w-3.5 h-3.5 mt-0.5" />
							<div>
								<p class="font-semibold">TOML Requirement Detected:</p>
								<p>This app specifies Frappe {{ frappeRequirement }}.</p>
							</div>
						</div>

						<div class="flex flex-wrap gap-2">
							<Badge v-for="app in dependencies" :key="app">
								{{ app }}
							</Badge>

							<div
								v-if="loadingMeta"
								class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400"
							>
								<LoadingIndicator class="w-4 h-4" />
								Scanning pyproject.toml…
							</div>

							<div
								v-else-if="!dependencies.length"
								class="text-sm text-gray-400 dark:text-gray-500 italic"
							>
								No dependencies declared
							</div>
						</div>
					</div>

					<div
						class="border border-gray-200 dark:border-gray-700 rounded-xl p-5 flex items-center gap-5 bg-white dark:bg-gray-800"
					>
						<div
							class="w-16 h-16 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center overflow-hidden"
						>
							<img
								v-if="form.logo"
								:src="form.logo"
								class="w-full h-full object-cover"
							/>
							<FeatherIcon
								v-else
								name="image"
								class="w-6 h-6 text-gray-400 dark:text-gray-500"
							/>
						</div>

						<div>
							<p class="text-sm font-medium text-gray-800 dark:text-gray-100">
								App Logo
							</p>
							<p class="text-xs text-gray-500 dark:text-gray-400 mb-2">
								Displayed on Marketplace listing
							</p>

							<FileUploader @success="(file) => (form.logo = file.file_url)">
								<template #default="{ openFileSelector, uploading, progress }">
									<Button
										size="sm"
										@click="openFileSelector"
										:loading="uploading"
									>
										{{ uploading ? `Uploading ${progress}%` : "Upload Logo" }}
									</Button>
								</template>
							</FileUploader>
						</div>
					</div>
				</div>
			</div>
		</section>

		<section>
			<div
				class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 space-y-6"
			>
				<div>
					<h2 class="text-lg font-semibold text-gray-900 dark:text-white">
						Compatibility Mapping
					</h2>
					<p class="text-sm text-gray-500 dark:text-gray-400">
						Map Frappe versions to the branch that supports them.
					</p>
				</div>

				<div
					class="grid grid-cols-[180px_40px_1fr_40px] text-xs text-gray-500 dark:text-gray-400 px-2"
				>
					<div>Frappe Version</div>
					<div></div>
					<div>Supported Branch</div>
					<div></div>
				</div>

				<div class="space-y-3">
					<div
						v-for="(row, index) in form.versions"
						:key="index"
						class="grid grid-cols-[180px_40px_1fr_40px] items-center gap-3 bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-3"
					>
						<Select
							:options="frappeVersionOptions"
							v-model="row.version"
							placeholder="Select version"
							:loading="versionsResource.loading"
						/>
						<div class="text-center text-gray-400">→</div>

						<Autocomplete
							:options="branchOptions"
							v-model="row.branch"
							placeholder="Search branch"
							:loading="loadingMeta"
						/>
						<Button variant="ghost" size="sm" @click="askRemove(index)">
							<FeatherIcon
								name="trash-2"
								class="w-4 h-4 text-red-500 hover:text-red-600"
							/>
						</Button>
					</div>
				</div>

				<div class="pt-2">
					<Button variant="outline" size="sm" @click="addRow">
						<template #prefix>
							<FeatherIcon name="plus" class="w-4 h-4" />
						</template>
						Add another version
					</Button>
				</div>
			</div>
		</section>
	</div>

	<Dialog
		v-model="showDeleteDialog"
		:options="{
			title: 'Delete version mapping?',
			message: 'This compatibility mapping will be permanently removed.',
			size: 'sm',
		}"
	>
		<template #actions>
			<Button variant="ghost" @click="showDeleteDialog = false"> Cancel </Button>

			<Button variant="solid" theme="red" @click="removeRowConfirmed"> Delete </Button>
		</template>
	</Dialog>
</template>

<script setup>
import { computed, ref } from "vue";
import {
	TextInput,
	Select,
	Badge,
	Button,
	FeatherIcon,
	FileUploader,
	LoadingIndicator,
	Autocomplete,
	createResource,
	Dialog,
} from "frappe-ui";

const showDeleteDialog = ref(false);
const rowToDelete = ref(null);

const props = defineProps([
	"form",
	"branches",
	"dependencies",
	"loadingMeta",
	"frappeRequirement",
]);

const branchOptions = computed(() => props.branches.map((b) => ({ label: b, value: b })));

const versionsResource = createResource({
	url: "frappe.client.get_list",
	params: {
		doctype: "Frappe Version",
		fields: ["name", "number"],
		filters: { public: 1 },
		order_by: "number desc",
	},
	auto: true,
});

const frappeVersionOptions = computed(() => {
	if (!versionsResource.data) return [];
	return versionsResource.data.map((v) => ({
		label: v.version_name || v.name,
		value: v.name,
	}));
});

function addRow() {
	props.form.versions.push({ version: "", branch: "" });
}

function askRemove(index) {
	rowToDelete.value = index;
	showDeleteDialog.value = true;
}

function removeRowConfirmed() {
	props.form.versions.splice(rowToDelete.value, 1);
	showDeleteDialog.value = false;
}
</script>
