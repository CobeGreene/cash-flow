<script setup lang="ts">
import { useCategoriesStore } from '@/store/categories_store'
import { storeToRefs } from 'pinia'
import { ref, computed, inject } from 'vue'
import { HttpService } from '@/service/http-service'
import CategoryPill from '@/components/CategoryPill.vue'
import AddCategoryPill from '@/components/AddCategoryPill.vue'
import AddSubCategoryPill from '@/components/AddSubCategoryPill.vue'

const categoriesStore = useCategoriesStore()
const {
	incomeEditSubCategories,
	investmentEditSubCategories,
	expensesEditCategories,
	ignoreEditSubCategories,
	editChanges,
} = storeToRefs(categoriesStore)
const http = inject<HttpService>('http')

const categoriesUpdated = computed(() => editChanges.value.length > 0)

const editingCategory = ref<string | null>(null)
const addingCategory = ref<string | null>(null)

function toggleEditCategory(cat: string) {
	editingCategory.value = cat
}
function cancelCategoryEdit() {
	editingCategory.value = null
}

function updateCategory(oldName: string, newName: string | null) {
	categoriesStore.updateCategory(oldName, newName)
	editingCategory.value = null
	addingCategory.value = null
}

function addingSubCategory(category: string | null) {
	addingCategory.value = category
}

function addSubCategory(category: string, subCategory: string | null) {
	addingCategory.value = null
	editingCategory.value = null
	categoriesStore.addSubCategory(category, subCategory)
}

function saveCategories() {
	http?.post('categories', { changes: editChanges.value })
		.then((data) => {
			// categoriesStore.loadCategories(data['data'])
			alert(`Categories updated successfully! ${data['data']}`)
		})
		.catch((error) => {
			console.error('Error updating categories:', error)
			alert('Failed to update categories. Please try again.')
		})
}
</script>

<template>
	<button
		class="btn btn-outline-primary mt-3"
		:disabled="!categoriesUpdated"
		@click="saveCategories()"
	>
		Save
	</button>
	<div class="category-pills-view mt-3">
		<h3>Income</h3>
		<div class="d-flex flex-wrap gap-2">
			<CategoryPill
				v-for="cat in incomeEditSubCategories"
				:key="cat"
				:label="cat"
				@edit-click="toggleEditCategory(cat)"
				@cancel-edit="cancelCategoryEdit()"
				@update-category="updateCategory(cat, $event)"
				@delete-category="updateCategory(cat, null)"
				:is-editing="editingCategory === cat"
			/>
			<AddSubCategoryPill
				:is-editing="addingCategory === 'Income'"
				:label="'Add Sub-Category'"
				@add-category="addSubCategory('Income', $event)"
				@cancel-edit="addingSubCategory(null)"
				@edit-click="addingSubCategory('Income')"
			/>
		</div>
		<hr />
		<h3>Investment</h3>
		<div class="d-flex flex-wrap gap-2">
			<CategoryPill
				v-for="cat in investmentEditSubCategories"
				:key="cat"
				:label="cat"
				@edit-click="toggleEditCategory(cat)"
				@cancel-edit="cancelCategoryEdit()"
				@update-category="updateCategory(cat, $event)"
				@delete-category="updateCategory(cat, null)"
				:is-editing="editingCategory === cat"
			/>
			<AddSubCategoryPill
				:is-editing="addingCategory === 'Investment'"
				:label="'Add Sub-Category'"
				@add-category="addSubCategory('Investment', $event)"
				@cancel-edit="addingSubCategory(null)"
				@edit-click="addingSubCategory('Investment')"
			/>
		</div>
		<hr />
		<h3>Expenses</h3>
		<template v-for="(value, key) in expensesEditCategories" :key="key">
			<h4>{{ key }}</h4>
			<div class="d-flex flex-wrap gap-2">
				<CategoryPill
					v-for="cat in value"
					:key="cat"
					:label="cat"
					@edit-click="toggleEditCategory(cat)"
					@cancel-edit="cancelCategoryEdit()"
					@update-category="updateCategory(cat, $event)"
					@delete-category="updateCategory(cat, null)"
					:is-editing="editingCategory === cat"
				/>
				<AddSubCategoryPill
					:is-editing="addingCategory === key"
					:label="'Add Sub-Category'"
					@add-category="addSubCategory(String(key), $event)"
					@cancel-edit="addingSubCategory(null)"
					@edit-click="addingSubCategory(String(key))"
				/>
			</div>
		</template>
		<div class="d-flex flex-wrap gap-2 mt-2">
			<AddSubCategoryPill
				:is-editing="addingCategory === 'New Category'"
				:label="'Add Category'"
				@add-category="addSubCategory($event, null)"
				@cancel-edit="addingSubCategory(null)"
				@edit-click="addingSubCategory('New Category')"
			/>
		</div>
		<hr />
		<h3>Ignore</h3>
		<div class="d-flex flex-wrap gap-2">
			<CategoryPill
				v-for="cat in ignoreEditSubCategories"
				:key="cat"
				:label="cat"
				@edit-click="toggleEditCategory(cat)"
				@cancel-edit="cancelCategoryEdit()"
				@update-category="updateCategory(cat, $event)"
				@delete-category="updateCategory(cat, null)"
				:is-editing="editingCategory === cat"
			/>
			<AddSubCategoryPill
				:is-editing="addingCategory === 'Ignore'"
				:label="'Add Sub-Category'"
				@add-category="addSubCategory('Ignore', $event)"
				@cancel-edit="addingSubCategory(null)"
				@edit-click="addingSubCategory('Ignore')"
			/>
		</div>
	</div>
</template>