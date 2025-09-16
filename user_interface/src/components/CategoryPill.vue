<script setup lang="ts">
import { defineProps } from 'vue'

const props = defineProps<{
	label: string
}>()
</script>

<template>
	<div class="d-inline-flex align-items-center me-2 mb-2 custom-chip-container">
		<span class="badge rounded-pill text-bg-primary p-2 me-1"> {{ props.label }} </span>
		<div class="custom-chip-actions d-flex">
			<button
				class="btn btn-sm btn-warning text-dark p-0 me-1 rounded-circle d-flex align-items-center justify-content-center custom-chip-action"
				title="Edit"
			>
				<i class="bi bi-check"></i>
			</button>
			<button
				class="btn btn-sm btn-danger text-dark p-0 me-1 rounded-circle d-flex align-items-center justify-content-center custom-chip-action"
				title="Delete"
			>
				<i class="bi bi-x"></i>
			</button>
		</div>
	</div>
</template>

<style scoped>
.custom-chip-actions {
	width: 0;
	transform: scale(0); /* Hidden by default, scaled to 0 */
	transition: transform 0.3s ease-in-out; /* Smooth transition */
}

.custom-chip-action {
	width: 28px;
	height: 28px;
}

.custom-chip-container {
	width: auto;
}

.custom-chip-container:hover .custom-chip-actions {
	width: auto;
	transform: scale(1); /* Visible on hover, scaled to 1 */
}

/* Optional: to make the badge lighter on hover */
.custom-chip-container:hover .badge {
	filter: brightness(115%);
}
</style>