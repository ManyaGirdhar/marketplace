<template>
	<div class="min-h-screen bg-gray-50 dark:bg-gray-950 flex flex-col">
		<header
			class="flex items-center justify-between px-6 py-4 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800"
		>
			<div class="flex items-center gap-2">
				<img src="" class="w-6 h-6" />
				<span class="font-semibold text-gray-900 dark:text-white"> Marketplace </span>
			</div>

			<Button variant="ghost" @click="goToDashboard"> Exit </Button>
		</header>

		<main class="flex-1 flex items-start justify-center p-6">
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
