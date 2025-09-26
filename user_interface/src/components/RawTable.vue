<script setup lang="ts">
import {
	useTransactionsStore,
	getDate,
	getName,
	getAmount,
	getCategory,
	getSubCategory,
	getMemo,
	getTransaction,
	getOriginalAmount,
	getOriginalDate,
	type Transaction,
} from '@/store/transactions_store'
import { useCategoriesStore } from '@/store/categories_store'
import { storeToRefs } from 'pinia'
import { ref, computed, watch, inject } from 'vue'
import { HttpService } from '@/service/http-service'
import moment from 'moment'

const http = inject<HttpService>('http')
const transactionsStore = useTransactionsStore()
const categoriesStore = useCategoriesStore()
const { transactions } = storeToRefs(transactionsStore)
const { allCategories, allSubCategories } = storeToRefs(categoriesStore)

const searchQuery = ref('')
const searchSubCategoriesQuery = ref('')
const debouncedQuery = ref('')
let debounceTimeout: ReturnType<typeof setTimeout> | null = null
const searchMode = ref('contains') // 'contains' or 'not-contains'

const minDate = ref('')
const maxDate = ref('')
const selectedCategories = ref<string[]>([])
const selectedSubCategories = ref<string[]>([])
const editAll = ref(false)

watch(searchQuery, (val) => {
	if (debounceTimeout) clearTimeout(debounceTimeout)
	debounceTimeout = setTimeout(() => {
		debouncedQuery.value = val
	}, 300)
})

function toggleCategory(cat: string) {
	const idx = selectedCategories.value.indexOf(cat)
	if (idx === -1) {
		selectedCategories.value.push(cat)
	} else {
		selectedCategories.value.splice(idx, 1)
	}
}
function toggleSubCategory(sub: string) {
	const idx = selectedSubCategories.value.indexOf(sub)
	if (idx === -1) {
		selectedSubCategories.value.push(sub)
	} else {
		selectedSubCategories.value.splice(idx, 1)
	}
}

const filteredTransactions = computed(() => {
	let filtered = transactions.value
	// Filter by name
	if (debouncedQuery.value) {
		const q = debouncedQuery.value.toLowerCase()
		if (searchMode.value === 'contains') {
			filtered = filtered.filter((item) => getName(item)?.toLowerCase().includes(q))
		} else {
			filtered = filtered.filter((item) => !getName(item)?.toLowerCase().includes(q))
		}
	}
	// Filter by min date
	if (minDate.value) {
		const min = new Date(minDate.value)
		filtered = filtered.filter((item) => new Date(getDate(item)) >= min)
	}
	// Filter by max date
	if (maxDate.value) {
		const max = new Date(maxDate.value)
		filtered = filtered.filter((item) => new Date(getDate(item)) <= max)
	}
	// Filter by category
	if (selectedCategories.value.length > 0) {
		filtered = filtered.filter((item) => selectedCategories.value.includes(getCategory(item)))
	}
	// Filter by sub-category
	if (selectedSubCategories.value.length > 0) {
		filtered = filtered.filter((item) =>
			selectedSubCategories.value.includes(getSubCategory(item))
		)
	}
	return filtered
})

// Pagination state and logic
const pageSize = 50
const currentPage = ref(1)
const pageCount = computed(() => Math.ceil(filteredTransactions.value.length / pageSize))
const paginatedTransactions = computed(() => {
	const start = (currentPage.value - 1) * pageSize
	return filteredTransactions.value.slice(start, start + pageSize)
})

function goToPage(page: number) {
	if (page >= 1 && page <= pageCount.value) {
		selectedRows.value.clear()
		currentPage.value = page
	}
}
// Table selection
const selectedRows = ref<Set<number>>(new Set())

function toggleRowSelection(rowIndex: number) {
	if (selectedRows.value.has(rowIndex)) {
		selectedRows.value.delete(rowIndex)
	} else {
		selectedRows.value.add(rowIndex)
	}
}

function toggleEditAll() {
	editAll.value = !editAll.value
	if (!editAll.value) {
		selectedRows.value.clear()
	}
}

function bulkUpdateSubCategory(newSubCategory: string) {
	const transactionsToUpdates: {
		Date: string
		Name: string
		Memo: string
		Transaction: string
		Amount: string
		Category: string
		'Sub Category': string
	}[] = []
	const newCategory = categoriesStore.getCategoryOfSubCategory(newSubCategory)
	if (!newCategory) {
		alert(`Sub-category "${newSubCategory}" does not have a corresponding category.`)
		return
	}
	if (editAll.value) {
		paginatedTransactions.value.forEach((t) => {
			if (getSubCategory(t) !== newSubCategory) {
				transactionsToUpdates.push({
					Date: getOriginalDate(t),
					Name: getName(t),
					Memo: getMemo(t),
					Transaction: getTransaction(t),
					Amount: getOriginalAmount(t),
					Category: newCategory,
					'Sub Category': newSubCategory,
				})
			}
		})
	} else {
		selectedRows.value.forEach((idx) => {
			const t = filteredTransactions.value[idx]
			if (t && getSubCategory(t) !== newSubCategory) {
				transactionsToUpdates.push({
					Date: getOriginalDate(t),
					Name: getName(t),
					Memo: getMemo(t),
					Transaction: getTransaction(t),
					Amount: getOriginalAmount(t),
					Category: newCategory,
					'Sub Category': newSubCategory,
				})
			}
		})
	}
	if (transactionsToUpdates.length === 0) {
		alert('No transactions to update.')
		return
	}
	http?.post('update_transactions_categories', {
		rows: transactionsToUpdates,
	}).then((data) => {
		transactionsStore.loadTransactions(data['data'])
	})
}

function train() {
	http?.post('train').then((data) => {
		console.log('Training started:', data)
	})
}

watch(filteredTransactions, () => {
	currentPage.value = 1
	selectedRows.value.clear()
})
</script>


<template>
	<div class="search-query">
		<div class="search-bar-row">
			<input
				v-model="searchQuery"
				type="text"
				class="form-control search-input"
				placeholder="Search by name..."
			/>
			<select v-model="searchMode" class="form-select search-mode-select">
				<option value="contains">CONTAINS</option>
				<option value="not-contains">NOT CONTAINS</option>
			</select>
		</div>
		<div class="date-picker-row">
			<label class="date-label">
				Min Date:
				<input type="date" v-model="minDate" class="form-control date-input" />
			</label>
			<label class="date-label">
				Max Date:
				<input type="date" v-model="maxDate" class="form-control date-input" />
			</label>
			<div class="dropdown-label">
				<span>Category:</span>
				<div class="dropdown">
					<button
						class="btn btn-outline-secondary dropdown-toggle"
						type="button"
						data-bs-toggle="dropdown"
						aria-expanded="false"
					>
						{{
							selectedCategories.length === 0 ? 'All' : selectedCategories.join(', ')
						}}
					</button>
					<ul class="dropdown-menu">
						<li v-for="cat in allCategories" :key="cat">
							<a href="#" class="dropdown-item" @click.prevent="toggleCategory(cat)">
								<span v-if="selectedCategories.includes(cat)">✔ </span>{{ cat }}
							</a>
						</li>
					</ul>
				</div>
			</div>

			<div class="dropdown-label">
				<span>Sub Category:</span>
				<div class="dropdown">
					<button
						class="btn btn-outline-secondary dropdown-toggle"
						type="button"
						data-bs-toggle="dropdown"
						aria-expanded="false"
					>
						{{
							selectedSubCategories.length === 0
								? 'All'
								: selectedSubCategories.join(', ')
						}}
					</button>
					<ul class="dropdown-menu">
						<li v-for="sub in allSubCategories" :key="sub">
							<a
								href="#"
								class="dropdown-item"
								@click.prevent="toggleSubCategory(sub)"
							>
								<span v-if="selectedSubCategories.includes(sub)">✔ </span>{{ sub }}
							</a>
						</li>
					</ul>
				</div>
			</div>
			<button class="btn btn-outline-success" type="button" @click.prevent="train()">
				Train
			</button>
		</div>
	</div>

	<table class="table table-striped table-hover">
		<thead class="thead-dark">
			<tr>
				<th scope="col">
					<input type="checkbox" @click="toggleEditAll" />
				</th>
				<th scope="col" class="col-1">Date</th>
				<th scope="col" class="col-5">Name</th>
				<th scope="col" class="col-1">Amount</th>
				<th scope="col" class="col-2">Category</th>
				<th scope="col" class="col-3">
					<div v-if="editAll || selectedRows.size > 0" class="dropdown">
						<button
							class="btn btn-sm btn-outline-primary dropdown-toggle p-0"
							type="button"
							data-bs-toggle="dropdown"
							aria-expanded="false"
						>
							Edit Sub-Category
						</button>
						<ul class="dropdown-menu">
							<input
								v-model="searchSubCategoriesQuery"
								type="text"
								class="form-control"
								placeholder="Search by name..."
							/>
							<div class="dropdown-menu-items">
								<template v-for="sub in allSubCategories" :key="sub">
									<li
										v-if="
											!searchSubCategoriesQuery ||
											sub
												.toLowerCase()
												.includes(searchSubCategoriesQuery.toLowerCase())
										"
									>
										<a
											href="#"
											class="dropdown-item"
											@click.prevent="bulkUpdateSubCategory(sub)"
										>
											{{ sub }}
										</a>
									</li>
								</template>
							</div>
						</ul>
					</div>
					<div v-else>Sub-Category</div>
				</th>
			</tr>
		</thead>
		<tbody>
			<tr
				v-for="(item, index) in paginatedTransactions"
				:key="(currentPage - 1) * pageSize + index"
				:class="{
					'table-active':
						editAll || selectedRows.has((currentPage - 1) * pageSize + index),
				}"
				@click="toggleRowSelection((currentPage - 1) * pageSize + index)"
			>
				<th scope="row">{{ (currentPage - 1) * pageSize + index + 1 }}</th>
				<td>{{ $moment(getDate(item)).format('YYYY-MM-DD') }}</td>
				<td>{{ getName(item) }}</td>
				<td>{{ getAmount(item) }}</td>
				<td>{{ getCategory(item) }}</td>
				<td>{{ getSubCategory(item) }}</td>
			</tr>
		</tbody>
	</table>

	<nav v-if="pageCount > 1" aria-label="Table pagination">
		<ul class="pagination justify-content-end">
			<li class="current-page">
				Page {{ currentPage }}
				of
				{{ pageCount }}
			</li>
			<li class="page-item" :class="{ disabled: currentPage === 1 }">
				<a class="page-link" href="#" @click.prevent="goToPage(currentPage - 1)"
					>Previous</a
				>
			</li>
			<li class="page-item" :class="{ disabled: currentPage === pageCount }">
				<a class="page-link" href="#" @click.prevent="goToPage(currentPage + 1)">Next</a>
			</li>
		</ul>
	</nav>
</template>

<style scoped>
.current-page {
	padding: 8px 12px;
}
.search-query {
	margin-bottom: 20px;
}
.search-bar-row {
	display: flex;
	gap: 10px;
	align-items: center;
	margin-bottom: 10px;
}
.search-input {
	flex: 1;
}
.search-mode-select {
	width: 200px;
}
.date-picker-row {
	display: flex;
	gap: 10px;
	align-items: center;
	margin-bottom: 10px;
}
.date-label {
	display: flex;
	align-items: center;
	gap: 5px;
}
.date-input {
	width: auto;
	display: inline-block;
}
.dropdown-label {
	display: flex;
	align-items: center;
	gap: 5px;
	margin-right: 10px;
}
.dropdown-toggle {
	width: 200px;
	max-width: 200px;
	text-overflow: ellipsis;
	overflow: hidden;
	white-space: nowrap;
	display: inline-block;
	vertical-align: middle;
}

.dropdown-menu .form-control {
	margin: 5px;
	width: auto;
}

.dropdown-menu-items {
	max-height: 150px;
	overflow-y: auto;
}

.table-hover tbody tr:hover {
	--bs-table-hover-bg: #3d8bfd; /* Your desired hover color */
}
.table-active {
	--bs-table-active-bg: #9ec5fe; /* Example: change to a yellow color */
	/* You can also adjust text color if needed */
	--bs-table-active-color: #212529; /* Dark text for better contrast */
}
</style>