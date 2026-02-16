<template>
	<div class="min-h-screen bg-gray-50 dark:bg-gray-950 flex flex-col">
		<header class="px-6 pt-6 pb-2 bg-gray-50 dark:bg-gray-950">
			<div class="max-w-4xl mx-auto flex items-center justify-between">
				<Button
					@click="goToDashboard"
					class="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
				>
					← Back to dashboard
				</Button>

				<Button @click="$emit('continue')" v-if="$slots.actions">
					<slot name="actions" />
				</Button>
			</div>
		</header>

		<main class="flex-1 flex justify-center px-6 pb-10">
			<div class="w-full max-w-4xl">
				<router-view />
			</div>
		</main>
	</div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();

function goToDashboard() {
	router.push("/dashboard/my-apps");
}
</script>
