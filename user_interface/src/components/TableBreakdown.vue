<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { getDate, useTransactionsStore } from '@/store/transactions_store'
import { useCategoriesStore } from '@/store/categories_store'
import { computed } from 'vue'
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
	name: string
	level: RowLevel
	category: string | null
	subCategory: string | null
}

const tableBreakdown = computed(() => {
	const result = [] as (RowHeader | string)[][]
	result.push([{ name: props.timeUnit, level: RowLevel.Top, category: null, subCategory: null }])
	result.push([{ name: 'Income', level: RowLevel.Top, category: 'Income', subCategory: null }])
	for (const subCategory of categories.value['Income'] || []) {
		result.push([{ name: subCategory, level: RowLevel.Sub, category: 'Income', subCategory }])
	}
	result.push([
		{ name: 'Investment', level: RowLevel.Top, category: 'Investment', subCategory: null },
	])
	for (const subCategory of categories.value['Investment'] || []) {
		result.push([
			{ name: subCategory, level: RowLevel.Sub, category: 'Investment', subCategory },
		])
	}
	result.push([
		{ name: 'Expenses', level: RowLevel.Top, category: 'Expenses', subCategory: null },
	])
	for (const category of Object.keys(categories.value)) {
		if (['Income', 'Investment', 'Ignore'].includes(category)) {
			continue
		}
		result.push([{ name: category, level: RowLevel.Mid, category, subCategory: null }])
		for (const subCategory of categories.value[category]) {
			result.push([{ name: subCategory, level: RowLevel.Sub, category, subCategory }])
		}
	}

	let startDate = props.getPreviousTime(props.getPreviousTime(props.currentDate))
	const endDate = props.getNextTime(props.getNextTime(props.currentDate))

	while (startDate <= endDate) {
		const transactionsInTime = transactions.value.filter((transaction) =>
			props.isSameTimeAsCurrentDate(getDate(transaction), startDate)
		)
		result[0].push(props.getFormatTime(startDate))
		for (let i = 1; i < result.length; i++) {
			const rowHeader = result[i][0] as RowHeader
			let sliceFunc = createSliceFunc(rowHeader.category, rowHeader.subCategory, true)
			if (rowHeader.category == 'Income') {
				sliceFunc = createSliceFunc(rowHeader.category, rowHeader.subCategory, false)
			} else if (rowHeader.name == 'Expenses') {
				sliceFunc = expensesSliceFunc
			}
			result[i].push(
				// eslint-disable-next-line @typescript-eslint/no-unused-vars
				totalBreakdownAmount(transactionsInTime, sliceFunc, (_: Date) => true).toFixed(2)
			)
		}

		startDate = props.getNextTime(startDate)
	}

	return result
})

function getRowHeader(row: (string | RowHeader)[]): RowHeader {
	return row[0] as RowHeader
}
</script>

<template>
	<table class="table table-striped">
		<thead>
			<tr>
				<th scope="col">Category</th>
				<th v-for="(header, index) in tableBreakdown[0].slice(1)" :key="index">
					{{ header }}
				</th>
			</tr>
		</thead>
		<tbody>
			<tr v-for="(row, rowIndex) in tableBreakdown.slice(1)" :key="rowIndex">
				<td
					:style="{
						'text-align': 'left',
						'font-weight':
							getRowHeader(row).level === 'Top'
								? 'bold'
								: getRowHeader(row).level === 'Mid'
								? '600'
								: 'normal',
						'padding-left': getRowHeader(row).level === 'Sub' ? '20px' : '10px',
					}"
				>
					{{ getRowHeader(row).name }}
				</td>
				<td v-for="(value, index) in row.slice(1)" :key="index">${{ value }}</td>
			</tr>
		</tbody>
	</table>
</template>