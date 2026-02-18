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
type RowValue = {
	value: string
	percentageChange: string
	isPositive: boolean
}

const tableBreakdown = computed(() => {
	const result = [] as (RowHeader | RowValue)[][]
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
	let previousStartDate = props.getPreviousTime(startDate)
	const endDate = props.getNextTime(props.getNextTime(props.currentDate))

	while (startDate <= endDate) {
		const transactionsInTime = transactions.value.filter((transaction) =>
			props.isSameTimeAsCurrentDate(getDate(transaction), startDate)
		)
		const transactionsPreviousTime = transactions.value.filter((transaction) =>
			props.isSameTimeAsCurrentDate(getDate(transaction), previousStartDate)
		)
		result[0].push({
			value: props.getFormatTime(startDate),
			isPositive: true,
			percentageChange: '0',
		})
		for (let i = 1; i < result.length; i++) {
			const rowHeader = result[i][0] as RowHeader
			let inverse = -1
			let sliceFunc = createSliceFunc(rowHeader.category, rowHeader.subCategory, true)
			if (rowHeader.category == 'Income') {
				inverse = 1
				sliceFunc = createSliceFunc(rowHeader.category, rowHeader.subCategory, false)
			} else if (rowHeader.category == 'Investment') {
				inverse = 1
			} else if (rowHeader.name == 'Expenses') {
				sliceFunc = expensesSliceFunc
			}
			const currentValue = totalBreakdownAmount(
				transactionsInTime,
				sliceFunc,
				// eslint-disable-next-line @typescript-eslint/no-unused-vars
				(_: Date) => true
			)
			const previousValue = totalBreakdownAmount(
				transactionsPreviousTime,
				sliceFunc,
				// eslint-disable-next-line @typescript-eslint/no-unused-vars
				(_: Date) => true
			)
			let percentageChange = 0
			if (previousValue !== 0) {
				percentageChange = (currentValue - previousValue) / Math.abs(previousValue)
			}
			result[i].push({
				value: currentValue.toFixed(2),
				percentageChange: (percentageChange * 100).toFixed(2),
				isPositive: percentageChange * inverse >= 0,
			})
		}

		startDate = props.getNextTime(startDate)
		previousStartDate = props.getNextTime(previousStartDate)
	}

	return result
})

function getRowHeader(row: (RowValue | RowHeader)[]): RowHeader {
	return row[0] as RowHeader
}
function getRowValue(value: RowValue | RowHeader): string {
	return (value as RowValue).value
}
function getRowPercentageChange(value: RowValue | RowHeader): string {
	return (value as RowValue).percentageChange
}
function getRowValueIsPositive(value: RowValue | RowHeader): boolean {
	return (value as RowValue).isPositive
}
</script>

<template>
	<table class="table table-striped">
		<thead>
			<tr>
				<th scope="col">Category</th>
				<th v-for="(header, index) in tableBreakdown[0].slice(1)" :key="index">
					{{ getRowValue(header) }}
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
				<td v-for="(value, index) in row.slice(1)" :key="index">
					${{ getRowValue(value) }}
					<span
						:class="{
							'text-success': getRowValueIsPositive(value),
							'text-danger': !getRowValueIsPositive(value),
						}"
						>( {{ getRowPercentageChange(value) }}%)</span
					>
				</td>
			</tr>
		</tbody>
	</table>
</template>

