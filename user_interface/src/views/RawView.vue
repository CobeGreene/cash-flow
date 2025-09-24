<script setup lang="ts">
import { ref } from 'vue'
import CategoryEditor from '@/components/CategoryEditor.vue'
import RawTable from '@/components/RawTable.vue'
import { useCategoriesStore } from '@/store/categories_store'

const showTable = ref(true) // true: show table, false: show category pills
function toggleView() {
	showTable.value = !showTable.value
	if (!showTable.value) {
		useCategoriesStore().restoreEditCategories()
	}
}
</script>

<template>
	<h1>Raw</h1>
	<ul class="nav nav-tabs">
		<li class="nav-item">
			<a
				class="nav-link"
				:class="{ active: showTable }"
				aria-current="page"
				href="#"
				@click="toggleView"
				>Transactions</a
			>
		</li>
		<li class="nav-item">
			<a
				class="nav-link"
				:class="{ active: !showTable }"
				aria-current="page"
				href="#"
				@click="toggleView"
				>Categories</a
			>
		</li>
	</ul>
	<template v-if="showTable">
		<RawTable></RawTable>
	</template>

	<template v-else>
		<CategoryEditor></CategoryEditor>
	</template>
</template>
