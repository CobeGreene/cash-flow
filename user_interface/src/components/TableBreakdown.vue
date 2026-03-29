<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { getDate, useTransactionsStore } from '@/store/transactions_store'
import { useCategoriesStore } from '@/store/categories_store'
import {
	createSliceFunc,
	expensesSliceFunc,
	totalBreakdownAmount,
} from '@/helper/transactions_utils'

const store = useTransactionsStore()
const { transactions } = storeToRefs(store)
const categoriesStore = useCategoriesStore()
const { categories } = storeToRefs(categoriesStore)

type TimeFunction = (date: Date, currentDate: Date) => boolean

const props = defineProps<{
	currentDate: Date
	isSameTimeAsCurrentDate: TimeFunction
	getNextTime: (date: Date) => Date
	getPreviousTime: (date: Date) => Date
	getFormatTime: (date: Date) => string
	timeUnit: string
}>()

enum RowLevel {
	Top = 'Top',
	Mid = 'Mid',
	Sub = 'Sub',
}

type RowHeader = {
	id: string // Unique identifier for the row
	name: string
	level: RowLevel
	category: string | null
	subCategory: string | null
}

type RowValue = {
	value: string
	percentageChange: string
	isPositive: boolean
}

type TableRow = {
	header: RowHeader
	values: RowValue[]
	children?: TableRow[]
}

const expandedRows = ref<Set<string>>(new Set())

// Initialize expandedRows on component mount
onMounted(() => {
    // Add top-level categories
    expandedRows.value.add('Income');
    expandedRows.value.add('Investment');
    expandedRows.value.add('Expenses');
});

// Watch for changes in `categories.value` to set default expanded state for dynamic mid-level categories
watch(categories, (newCategories) => {
    // Only set defaults for categories that are not yet in expandedRows
    for (const category of Object.keys(newCategories)) {
        if (!['Income', 'Investment', 'Ignore'].includes(category) && !expandedRows.value.has(category)) {
            expandedRows.value.add(category);
        }
    }
}, { immediate: true }); // immediate: true will run the watcher once on component creation

const toggleRow = (id: string) => {
	if (expandedRows.value.has(id)) {
		expandedRows.value.delete(id)
	} else {
		expandedRows.value.add(id)
	}
}

const isRowExpanded = (id: string) => expandedRows.value.has(id)

const tableBreakdown = computed(() => {
	const result: TableRow[] = []
	const timeUnitRow: TableRow = {
		header: { id: 'timeUnit', name: props.timeUnit, level: RowLevel.Top, category: null, subCategory: null },
		values: [],
	}
	result.push(timeUnitRow)

	// Income
	const incomeRow: TableRow = {
		header: { id: 'Income', name: 'Income', level: RowLevel.Top, category: 'Income', subCategory: null },
		values: [],
		children: [],
	}

	for (const subCategory of categories.value['Income'] || []) {
		incomeRow.children?.push({
			header: { id: `Income-${subCategory}`, name: subCategory, level: RowLevel.Sub, category: 'Income', subCategory },
			values: [],
		})
	}
	result.push(incomeRow)

	// Investment
	const investmentRow: TableRow = {
		header: { id: 'Investment', name: 'Investment', level: RowLevel.Top, category: 'Investment', subCategory: null },
		values: [],
		children: [],
	}

	for (const subCategory of categories.value['Investment'] || []) {
		investmentRow.children?.push({
			header: { id: `Investment-${subCategory}`, name: subCategory, level: RowLevel.Sub, category: 'Investment', subCategory },
			values: [],
		})
	}
	result.push(investmentRow)

	// Expenses
	const expensesRow: TableRow = {
		header: { id: 'Expenses', name: 'Expenses', level: RowLevel.Top, category: 'Expenses', subCategory: null },
		values: [],
		children: [],
	}

	for (const category of Object.keys(categories.value)) {
		if (['Income', 'Investment', 'Ignore'].includes(category)) {
			continue
		}
		const midRow: TableRow = {
			header: { id: category, name: category, level: RowLevel.Mid, category, subCategory: null },
			values: [],
			children: [],
		}

		for (const subCategory of categories.value[category]) {
			midRow.children?.push({
				header: { id: `${category}-${subCategory}`, name: subCategory, level: RowLevel.Sub, category, subCategory },
				values: [],
			})
		}
		expensesRow.children?.push(midRow)
	}
	result.push(expensesRow)

	let startDate = props.getPreviousTime(props.getPreviousTime(props.currentDate))
	let previousStartDate = props.getPreviousTime(startDate)
	const endDate = props.getNextTime(props.getNextTime(props.currentDate))

	while (startDate <= endDate) {
		const transactionsInTime = transactions.value.filter((transaction) => {
			return props.isSameTimeAsCurrentDate(getDate(transaction), startDate)
		})
		const transactionsPreviousTime = transactions.value.filter((transaction) =>
			props.isSameTimeAsCurrentDate(getDate(transaction), previousStartDate)
		)

		timeUnitRow.values.push({
			value: props.getFormatTime(startDate),
			isPositive: true,
			percentageChange: '0',
		})

		const fillRowValues = (row: TableRow) => {
			let inverse = -1
			let sliceFunc = createSliceFunc(row.header.category, row.header.subCategory, true)
			if (row.header.category == 'Income') {
				inverse = 1
				sliceFunc = createSliceFunc(row.header.category, row.header.subCategory, false)
			} else if (row.header.category == 'Investment') {
				inverse = 1
			} else if (row.header.name == 'Expenses') {
				sliceFunc = expensesSliceFunc
			}

			const currentValue = totalBreakdownAmount(
				transactionsInTime,
				sliceFunc,
				(_: Date) => true
			)
			const previousValue = totalBreakdownAmount(
				transactionsPreviousTime,
				sliceFunc,
				(_: Date) => true
			)
			let percentageChange = 0
			if (previousValue !== 0) {
				percentageChange = (currentValue - previousValue) / Math.abs(previousValue)
			}
			row.values.push({
				value: currentValue.toFixed(2),
				percentageChange: (percentageChange * 100).toFixed(2),
				isPositive: percentageChange * inverse >= 0,
			})

			row.children?.forEach(fillRowValues)
		}

		result.slice(1).forEach(fillRowValues) // Skip timeUnitRow

		startDate = props.getNextTime(startDate)
		previousStartDate = props.getNextTime(previousStartDate)
	}

	return result
})
</script>

<template>
	<table class="table table-striped">
		<thead>
			<tr>
				<th scope="col">{{ tableBreakdown[0].header.name }}</th>
				<th v-for="(value, index) in tableBreakdown[0].values" :key="index">
					{{ value.value }}
				</th>
			</tr>
		</thead>
		<tbody>
			<template v-for="row in tableBreakdown.slice(1)" :key="row.header.id">
				<tr :class="{'table-active': row.header.level === 'Top' || row.header.level === 'Mid'}">
					<td
						:style="{
							'text-align': 'left',
							'font-weight':
								row.header.level === 'Top'
									? 'bold'
									: row.header.level === 'Mid'
									? '600'
									: 'normal',
							'padding-left': row.header.level === 'Sub' ? '20px' : '10px',
						}"
					>
						<span
							v-if="row.children && row.children.length > 0"
							@click="toggleRow(row.header.id)"
							style="cursor: pointer; margin-right: 5px;"
						>
							{{ isRowExpanded(row.header.id) ? '▾' : '▸' }}
						</span>
						{{ row.header.name }}
					</td>
					<td v-for="(value, index) in row.values" :key="index">
						${{ value.value }}
						<span
							:class="{
								'text-success': value.isPositive,
								'text-danger': !value.isPositive,
							}"
							>( {{ value.percentageChange }}%)</span
						>
					</td>
				</tr>
				<template v-if="isRowExpanded(row.header.id) && row.children && row.children.length > 0">
					<template v-for="childRow in row.children" :key="childRow.header.id">
						<tr>
							<td
								:style="{
									'text-align': 'left',
									'font-weight':
										childRow.header.level === 'Top'
											? 'bold'
											: childRow.header.level === 'Mid'
											? '600'
											: 'normal',
									'padding-left': childRow.header.level === 'Sub' ? '40px' : '20px',
								}"
							>
								<span
									v-if="childRow.children && childRow.children.length > 0"
									@click="toggleRow(childRow.header.id)"
									style="cursor: pointer; margin-right: 5px;"
								>
									{{ isRowExpanded(childRow.header.id) ? '▾' : '▸' }}
								</span>
								{{ childRow.header.name }}
							</td>
							<td v-for="(value, index) in childRow.values" :key="index">
								${{ value.value }}
								<span
									:class="{
										'text-success': value.isPositive,
										'text-danger': !value.isPositive,
									}"
									>( {{ value.percentageChange }}%)</span
								>
							</td>
						</tr>
						<template v-if="isRowExpanded(childRow.header.id) && childRow.children && childRow.children.length > 0">
							<tr v-for="subChildRow in childRow.children" :key="subChildRow.header.id">
								<td
									:style="{
										'text-align': 'left',
										'font-weight': 'normal',
										'padding-left': '60px',
									}"
								>
									{{ subChildRow.header.name }}
								</td>
								<td v-for="(value, index) in subChildRow.values" :key="index">
									${{ value.value }}
									<span
										:class="{
											'text-success': value.isPositive,
											'text-danger': !value.isPositive,
										}"
										>( {{ value.percentageChange }}%)</span
									>
								</td>
							</tr>
						</template>
					</template>
				</template>
			</template>
		</tbody>
	</table>
</template>
