<script setup lang="ts">
import { defineProps, defineEmits, ref } from 'vue'

const emit = defineEmits(['editClick', 'updateCategory', 'deleteCategory', 'cancelEdit'])

const props = defineProps<{
	label: string
	isEditing?: boolean
}>()

const newCategoryName = ref<string>('')

function handleEditClick() {
	newCategoryName.value = props.label
	emit('editClick')
}

function handleUpdateCategory() {
	emit('updateCategory', newCategoryName.value)
}

function handleDeleteCategory() {
	emit('deleteCategory')
}

function handleCancelEdit() {
	emit('cancelEdit')
}
</script>

<template>
	<div class="d-inline-flex align-items-center me-2 mb-2 custom-chip-container">
		<template v-if="props.isEditing">
			<span class="badge rounded-pill text-bg-primary p-2 me-1">
				<input type="text" v-model="newCategoryName" class="form-control form-control-sm" />
			</span>
			<div class="d-flex">
				<button
					class="btn btn-sm btn-danger text-dark p-0 me-1 rounded-circle d-flex align-items-center justify-content-center custom-chip-action"
					title="Cancel"
					@click="handleCancelEdit()"
				>
					<i class="bi bi-x"></i>
				</button>
				<button
					class="btn btn-sm btn-warning text-dark p-0 me-1 rounded-circle d-flex align-items-center justify-content-center custom-chip-action"
					title="Save"
					@click="handleUpdateCategory()"
				>
					<i class="bi bi-check"></i>
				</button>
			</div>
		</template>
		<template v-else>
			<span class="badge rounded-pill text-bg-primary p-2 me-1"> {{ props.label }} </span>
			<div class="custom-chip-actions d-flex">
				<button
					class="btn btn-sm btn-warning text-dark p-0 me-1 rounded-circle d-flex align-items-center justify-content-center custom-chip-action"
					title="Edit"
					@click="handleEditClick()"
				>
					<i class="bi bi-pencil"></i>
				</button>
				<button
					class="btn btn-sm btn-danger text-dark p-0 me-1 rounded-circle d-flex align-items-center justify-content-center custom-chip-action"
					title="Delete"
					@click="handleDeleteCategory()"
				>
					<i class="bi bi-trash3"></i>
				</button>
			</div>
		</template>
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