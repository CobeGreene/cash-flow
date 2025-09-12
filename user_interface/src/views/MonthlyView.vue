<script setup lang="ts">
import { storeToRefs } from 'pinia'
import PieChart from '@/components/PieChart.vue'
import ScoreCard from '@/components/ScoreCard.vue'
import LineChart from '@/components/LineChart.vue'
import {
	getAmount,
	getCategory,
	getDate,
	getSubCategory,
	useTransactionsStore,
} from '@/store/transactions_store'
import { computed, ref, watch } from 'vue'
import moment from 'moment'
import {
	breakdown,
	expensesSliceFunc,
	grocerySliceFunc,
	incomeSliceFunc,
	investingSliceFunc,
	miscellaneousSliceFunc,
	scoreCard,
	totalBreakdownAmount,
} from '@/helper/transactions_utils'

const store = useTransactionsStore()
const { transactions, maxDate, hasData } = storeToRefs(store)
const currentDate = ref<Date | undefined>()

currentDate.value = maxDate.value

watch(hasData, (_value, _oldValue) => {
	currentDate.value = maxDate.value
})

function isSameMonthAsCurrentDate(date: Date, currentDate: Date) {
	return (
		currentDate.getMonth() === date.getMonth() &&
		currentDate.getFullYear() === date.getFullYear()
	)
}

function isPreviousMonthAsCurrentDate(date: Date) {
	const previousDate = new Date(currentDate.value || new Date())
	previousDate.setMonth(previousDate.getMonth() - 1)
	return (
		previousDate.getMonth() === date.getMonth() &&
		previousDate.getFullYear() === date.getFullYear()
	)
}
function isNextMonthAsCurrentDate(date: Date) {
	const nextDate = new Date(currentDate.value || new Date())
	nextDate.setMonth(nextDate.getMonth() + 1)
	return nextDate.getMonth() === date.getMonth() && nextDate.getFullYear() === date.getFullYear()
}

const groceryBreakdown = computed(() => {
	return breakdown(transactions.value, grocerySliceFunc, (date: Date) =>
		isSameMonthAsCurrentDate(date, currentDate.value || new Date())
	)
})

const expensesScoreCard = computed(() => {
	return scoreCard(transactions.value, expensesSliceFunc, {
		current: (date) => isSameMonthAsCurrentDate(date, currentDate.value || new Date()),
		next: isNextMonthAsCurrentDate,
		previous: isPreviousMonthAsCurrentDate,
	})
})

const groceryScoreCard = computed(() => {
	return scoreCard(transactions.value, grocerySliceFunc, {
		current: (date) => isSameMonthAsCurrentDate(date, currentDate.value || new Date()),
		next: isNextMonthAsCurrentDate,
		previous: isPreviousMonthAsCurrentDate,
	})
})

const miscellaneousScoreCard = computed(() => {
	return scoreCard(transactions.value, miscellaneousSliceFunc, {
		current: (date) => isSameMonthAsCurrentDate(date, currentDate.value || new Date()),
		next: isNextMonthAsCurrentDate,
		previous: isPreviousMonthAsCurrentDate,
	})
})

const expensesBreakdown = computed(() => {
	const b = breakdown(transactions.value, expensesSliceFunc, (date: Date) =>
		isSameMonthAsCurrentDate(date, currentDate.value || new Date())
	)
	return b
})

const miscellaneousBreakdown = computed(() => {
	return breakdown(transactions.value, miscellaneousSliceFunc, (date: Date) =>
		isSameMonthAsCurrentDate(date, currentDate.value || new Date())
	)
})

const subtractMonth = () => {
	if (currentDate.value) {
		const newDate = new Date(currentDate.value)
		newDate.setMonth(newDate.getMonth() - 1)
		currentDate.value = newDate
	}
}

const addMonth = () => {
	if (currentDate.value) {
		const newDate = new Date(currentDate.value)
		newDate.setMonth(newDate.getMonth() + 1)
		currentDate.value = newDate
	}
}

const incomeExpensesBreakdown = computed(() => {
	const dates = ['Category']
	const income = ['Income'] as (string | number)[]
	const expenses = ['Expenses'] as (string | number)[]
	const investing = ['Investing'] as (string | number)[]

	const startDate = new Date(currentDate?.value || new Date())
	startDate.setMonth(startDate.getMonth() - 2)
	const endDate = new Date(currentDate?.value || new Date())
	endDate.setMonth(endDate.getMonth() + 2)

	while (startDate <= endDate) {
		dates.push(moment(startDate).format('MMMM YYYY'))
		income.push(
			totalBreakdownAmount(transactions.value, incomeSliceFunc, (date: Date) =>
				isSameMonthAsCurrentDate(date, startDate)
			)
		)
		expenses.push(
			totalBreakdownAmount(transactions.value, expensesSliceFunc, (date: Date) =>
				isSameMonthAsCurrentDate(date, startDate)
			)
		)
		investing.push(
			totalBreakdownAmount(transactions.value, investingSliceFunc, (date: Date) =>
				isSameMonthAsCurrentDate(date, startDate)
			)
		)

		startDate.setMonth(startDate.getMonth() + 1)
	}

	return [dates, income, expenses, investing]
})
</script>

<template>
	<div class="container text-center">
		<div class="row align-items-center">
			<div class="col">
				<div class="btn-group" role="group">
					<button type="button" class="btn btn-outline-secondary" @click="subtractMonth">
						<i class="bi bi-caret-left"></i>
					</button>
					<button type="button" class="btn btn-outline-secondary month-button">
						{{ $moment(currentDate).format('MMMM YYYY') }}
					</button>
					<button type="button" class="btn btn-outline-secondary" @click="addMonth">
						<i class="bi bi-caret-right"></i>
					</button>
				</div>
			</div>
		</div>
	</div>
	<div class="income-charts">
		<LineChart :data="incomeExpensesBreakdown"></LineChart>
	</div>
	<div class="charts">
		<PieChart :title="'Expenses'" :data="expensesBreakdown"></PieChart>
		<PieChart :title="'Groceries'" :data="groceryBreakdown"></PieChart>
		<PieChart :title="'Miscellaneous'" :data="miscellaneousBreakdown"></PieChart>
	</div>
	<div class="scorecards">
		<ScoreCard
			:title="'Expenses'"
			:current-title="'Current Month'"
			:previous-title="'Previous Month'"
			:next-title="'Next Month'"
			:score-card="expensesScoreCard"
		>
		</ScoreCard>
		<ScoreCard
			:title="'Groceries'"
			:current-title="'Current Month'"
			:previous-title="'Previous Month'"
			:next-title="'Next Month'"
			:score-card="groceryScoreCard"
		>
		</ScoreCard>
		<ScoreCard
			:title="'Miscellaneous'"
			:current-title="'Current Month'"
			:previous-title="'Previous Month'"
			:next-title="'Next Month'"
			:score-card="miscellaneousScoreCard"
		>
		</ScoreCard>
	</div>
</template>

<style scoped>
.income-charts {
	display: grid;
	grid-template-columns: 1fr;
	grid-template-rows: 300px;
}

.charts {
	margin-top: 10px;
	display: grid;
	grid-template-columns: 1fr 1fr 1fr;
	grid-template-rows: minmax(200px, 1fr);
}

.scorecards {
	display: grid;
	grid-template-columns: 1fr 1fr 1fr;
	grid-template-rows: 1fr;
	column-gap: 30px;
}

.month-button {
	min-width: 200px;
}
</style>