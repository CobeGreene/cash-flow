<script setup lang="ts">
import { defineProps, defineEmits, ref } from 'vue'

const emit = defineEmits(['editClick', 'cancelEdit', 'addCategory'])

const props = defineProps<{
	isEditing?: boolean
}>()

const newCategoryName = ref<string>('')

function handleEditClick() {
	emit('editClick')
}

function handleAddCategory() {
	emit('addCategory', newCategoryName.value)
	newCategoryName.value = ''
}

function handleCancelEdit() {
	emit('cancelEdit')
}
</script>

<template>
	<div class="d-inline-flex align-items-center me-2 mb-2 custom-chip-container">
		<template v-if="!props.isEditing">
			<span @click="handleEditClick()" class="badge rounded-pill text-bg-success p-2 me-1">
				Add Sub-Category
			</span>
		</template>
		<template v-else>
			<span class="badge rounded-pill text-bg-success p-2 me-1">
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
					@click="handleAddCategory()"
				>
					<i class="bi bi-check"></i>
				</button>
			</div>
		</template>
	</div>
</template>

<style scoped>
.badge {
	cursor: pointer;
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
