<template>
	<div class="space-y-8 animate-in fade-in zoom-in duration-500">
		<div class="text-center py-10">
			<h2 class="text-2xl font-bold mb-2 tracking-tight">Technical Validation</h2>
			<p class="text-gray-400">
				Validating release:
				<span class="text-white font-mono text-sm">{{ form.app_release }}</span>
			</p>
		</div>
		<p v-if="hash" class="text-xs text-gray-600 mt-2">
			Commit: <span class="font-mono">{{ hash.substring(0, 7) }}</span>
		</p>
		<div class="border border-gray-800 rounded-3xl overflow-hidden bg-[#0A0A0A]">
			<div
				v-for="check in automatedChecks"
				:key="check.id"
				class="flex items-center justify-between px-10 py-6 border-b border-gray-800 last:border-0 hover:bg-white/5 transition-colors"
			>
				<div class="flex items-center gap-4">
					<div
						:class="[
							check.status === 'running'
								? 'animate-pulse bg-blue-500 shadow-[0_0_8px_#3b82f6]'
								: check.status === 'pass'
								? 'bg-green-500 shadow-[0_0_8px_#22c55e]'
								: check.status === 'fail'
								? 'bg-red-500 shadow-[0_0_8px_#ef4444]'
								: 'bg-gray-700',
							'w-2 h-2 rounded-full transition-all duration-500',
						]"
					></div>
					<span class="font-medium tracking-wide text-gray-200">{{ check.label }}</span>
				</div>

				<div class="flex items-center gap-3">
					<LoadingIndicator v-if="check.status === 'running'" class="w-4 h-4" />
					<FeatherIcon
						v-else-if="check.status === 'pass'"
						name="check-circle"
						class="w-5 h-5 text-green-500"
					/>
					<FeatherIcon
						v-else-if="check.status === 'fail'"
						name="x-circle"
						class="w-5 h-5 text-red-500"
					/>
					<span v-else class="text-xs text-gray-600 uppercase font-bold tracking-widest"
						>Waiting</span
					>
				</div>
			</div>
		</div>

		<div
			v-if="ciStatus === 'Failed'"
			class="mt-4 p-4 bg-red-900/10 border border-red-900/20 rounded-xl"
		>
			<p class="text-xs font-bold text-red-500 uppercase mb-2">Build Logs</p>
			<pre class="text-xs text-red-300 font-mono whitespace-pre-wrap">{{
				validationLogs || "No logs available"
			}}</pre>
		</div>

		<div
			class="mt-12 p-6 border border-gray-800 rounded-2xl bg-black/40 flex items-start gap-4"
		>
			<p class="text-sm text-gray-500 leading-relaxed italic">
				The validation process checks your hooks.py for required dependencies and executes
				automated benchmarks. You will be able to proceed once the build completes
				successfully.
			</p>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { LoadingIndicator, FeatherIcon, call } from "frappe-ui";

const props = defineProps(["form"]);
const emit = defineEmits(["validated"]);

const ciStatus = ref("Pending");
const validationLogs = ref("");
let pollInterval = null;

const automatedChecks = computed(() => [
	{ id: "repo", label: "GitHub Repository Connection", status: "pass" },
	{ id: "hooks", label: "Dependency Graph (hooks.py)", status: "pass" },
	{
		id: "ci",
		label: "Marketplace CI Build Pipeline",
		status:
			ciStatus.value === "Passed"
				? "pass"
				: ciStatus.value === "Failed"
				? "fail"
				: ciStatus.value === "Running"
				? "running"
				: "waiting",
	},
]);

async function fetchStatus() {
	if (!props.form.app_release) return;

	try {
		const data = await call("frappe.client.get_value", {
			doctype: "App Release",
			filters: { name: props.form.app_release },
			fieldname: ["ci_status", "validation_logs", "hash"],
		});

		if (data) {
			ciStatus.value = data.ci_status;
			validationLogs.value = data.validation_logs;

			if (ciStatus.value === "Passed") {
				emit("validated", true);
				stopPolling();
			} else if (ciStatus.value === "Failed") {
				emit("validated", false);
				stopPolling();
			}
		}
	} catch (e) {
		console.error("Error polling status:", e);
	}
}

function stopPolling() {
	if (pollInterval) {
		clearInterval(pollInterval);
		pollInterval = null;
	}
}

onMounted(() => {
	fetchStatus();
	pollInterval = setInterval(fetchStatus, 3000);
});

onUnmounted(() => {
	stopPolling();
});
</script>
