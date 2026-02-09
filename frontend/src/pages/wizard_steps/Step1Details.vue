<template>
	<div class="space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
		<section class="space-y-6">
			<h2 class="text-sm font-semibold uppercase tracking-widest text-gray-400">
				App Identity
			</h2>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-12">
				<div class="space-y-6">
					<div class="space-y-1">
						<TextInput
							label="App Title"
							v-model="form.app_title"
							placeholder="e.g. Airplane Mode"
						/>
						<p class="text-xs text-gray-500">
							Public name shown on Frappe Marketplace
						</p>
					</div>

					<div class="space-y-1">
						<TextInput
							label="App Name"
							v-model="form.app_name"
							variant="read-only"
							class="opacity-80"
						/>
						<p class="text-xs text-gray-500">Derived from repository (immutable)</p>
					</div>

					<div class="space-y-1">
						<TextInput
							label="Repository URL"
							v-model="form.repo_url"
							variant="read-only"
							class="opacity-80"
						/>
						<p class="text-xs text-gray-500">Used to fetch branches and metadata</p>
					</div>
				</div>

				<div class="space-y-6">
					<div class="p-6 border border-gray-800 rounded-2xl bg-[#0A0A0A]">
						<div class="flex items-center gap-2 mb-4">
							<FeatherIcon name="layers" class="w-4 h-4 text-gray-500" />
							<label
								class="text-xs uppercase font-semibold tracking-widest text-gray-400"
							>
								Detected Dependencies
							</label>
						</div>

						<div class="flex flex-wrap gap-2">
							<Badge
								v-for="app in dependencies"
								:key="app"
								theme="gray"
								variant="subtle"
							>
								{{ app }}
							</Badge>

							<div
								v-if="loadingMeta"
								class="flex items-center gap-2 text-gray-600 text-sm"
							>
								<LoadingIndicator class="w-4 h-4" />
								Scanning hooks.py…
							</div>

							<div
								v-else-if="!dependencies.length"
								class="text-gray-600 text-sm italic"
							>
								No dependencies declared
							</div>
						</div>
					</div>

					<div
						class="flex items-center gap-5 p-5 border border-gray-800 rounded-2xl bg-[#0A0A0A]"
					>
						<div
							class="w-16 h-16 rounded-xl bg-gray-900 border border-gray-800 flex items-center justify-center overflow-hidden"
						>
							<img
								v-if="form.logo"
								:src="form.logo"
								class="w-full h-full object-cover"
							/>
							<FeatherIcon v-else name="image" class="w-6 h-6 text-gray-700" />
						</div>

						<div class="space-y-1">
							<p class="text-sm font-medium text-gray-300">App Logo</p>
							<p class="text-xs text-gray-500">Displayed on Marketplace listing</p>

							<FileUploader @success="(file) => (form.logo = file.file_url)">
								<template #default="{ openFileSelector, uploading, progress }">
									<Button
										variant="subtle"
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

		<section class="space-y-4">
			<div class="flex items-start justify-between px-1">
				<div>
					<h3 class="text-sm font-semibold uppercase tracking-wider text-gray-400">
						Compatibility Mapping
					</h3>
					<p class="text-xs text-gray-500 mt-1">
						Map supported Frappe versions to compatible source branches
					</p>
				</div>

				<Button variant="ghost" size="sm" @click="addRow">
					<template #prefix>
						<FeatherIcon name="plus" class="w-3 h-3" />
					</template>
					Add Version
				</Button>
			</div>

			<div class="border border-gray-800 rounded-2xl overflow-hidden bg-[#0A0A0A]">
				<div
					class="grid grid-cols-12 bg-gray-900/50 px-6 py-3 border-b border-gray-800 text-xs font-bold text-gray-500 uppercase tracking-widest"
				>
					<div class="col-span-6">Frappe Version</div>
					<div class="col-span-5">Source Branch</div>
					<div class="col-span-1"></div>
				</div>

				<div
					v-for="(row, index) in form.versions"
					:key="index"
					class="grid grid-cols-12 px-6 py-4 border-b border-gray-800 last:border-0 items-center hover:bg-white/5 transition-colors"
				>
					<div class="col-span-6 pr-4">
						<Select
							:options="frappeVersionOptions"
							v-model="row.version"
							placeholder="Select Frappe Version"
							:loading="versionsResource.loading"
						/>
					</div>

					<div class="col-span-5 pr-4">
						<Select
							:options="branchOptions"
							v-model="row.branch"
							placeholder="Select Branch"
							:loading="loadingMeta"
						/>
					</div>

					<div class="col-span-1 text-right">
						<Button variant="ghost" @click="removeRow(index)">
							<template #icon>
								<FeatherIcon
									name="x"
									class="w-4 h-4 text-gray-600 hover:text-red-500"
								/>
							</template>
						</Button>
					</div>
				</div>
			</div>
		</section>
	</div>
</template>

<script setup>
import { computed } from "vue";
import {
	TextInput,
	Select,
	Badge,
	Button,
	FeatherIcon,
	FileUploader,
	LoadingIndicator,
	createResource,
} from "frappe-ui";

const props = defineProps(["form", "branches", "dependencies", "loadingMeta"]);

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

function removeRow(index) {
	props.form.versions.splice(index, 1);
}
</script>
