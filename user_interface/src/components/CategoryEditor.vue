<script setup lang="ts">
import { useCategoriesStore } from '@/store/categories_store'
import { storeToRefs } from 'pinia'
import { ref, computed, watch } from 'vue'
import CategoryPill from '@/components/CategoryPill.vue'
import AddSubCategoryPill from '@/components/AddSubCategoryPill.vue'

const categoriesStore = useCategoriesStore()
const { incomeSubCategories, investmentSubCategories, expensesCategories, ignoreSubCategories } =
	storeToRefs(categoriesStore)

const categoriesUpdated = ref<boolean>(false)
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
	categoriesUpdated.value = true
}

function addingSubCategory(category: string | null) {
	addingCategory.value = category
}

function addSubCategory(category: string, subCategory: string) {
	addingCategory.value = null
	editingCategory.value = null
	categoriesStore.addSubCategory(category, subCategory)
}
</script>

<template>
	<button class="btn btn-outline-primary mt-3" :disabled="!categoriesUpdated">Save</button>
	<div class="category-pills-view mt-3">
		<h3>Income</h3>
		<div class="d-flex flex-wrap gap-2">
			<CategoryPill
				v-for="cat in incomeSubCategories"
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
				@add-category="addSubCategory('Income', $event)"
				@cancel-edit="addingSubCategory(null)"
				@edit-click="addingSubCategory('Income')"
			/>
		</div>
		<hr />
		<h3>Investment</h3>
		<div class="d-flex flex-wrap gap-2">
			<CategoryPill
				v-for="cat in investmentSubCategories"
				:key="cat"
				:label="cat"
				@edit-click="toggleEditCategory(cat)"
				@cancel-edit="cancelCategoryEdit()"
				@update-category="updateCategory(cat, $event)"
				@delete-category="updateCategory(cat, null)"
			/>
			<AddSubCategoryPill
				:is-editing="addingCategory === 'Investment'"
				@add-category="addSubCategory('Investment', $event)"
				@cancel-edit="addingSubCategory(null)"
				@edit-click="addingSubCategory('Investment')"
			/>
		</div>
		<hr />
		<h3>Expenses</h3>
		<template v-for="(value, key) in expensesCategories" :key="key">
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
				/>
				<AddSubCategoryPill
					:is-editing="addingCategory === key"
					@add-category="addSubCategory(String(key), $event)"
					@cancel-edit="addingSubCategory(null)"
					@edit-click="addingSubCategory(String(key))"
				/>
			</div>
		</template>
		<hr />
		<h3>Ignore</h3>
		<div class="d-flex flex-wrap gap-2">
			<CategoryPill
				v-for="cat in ignoreSubCategories"
				:key="cat"
				:label="cat"
				@edit-click="toggleEditCategory(cat)"
				@cancel-edit="cancelCategoryEdit()"
				@update-category="updateCategory(cat, $event)"
				@delete-category="updateCategory(cat, null)"
			/>
			<AddSubCategoryPill
				:is-editing="addingCategory === 'Ignore'"
				@add-category="addSubCategory('Ignore', $event)"
				@cancel-edit="addingSubCategory(null)"
				@edit-click="addingSubCategory('Ignore')"
			/>
		</div>
	</div>
</template>