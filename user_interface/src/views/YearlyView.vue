<script setup lang="ts">
import { storeToRefs } from 'pinia'
import PieChart from '@/components/PieChart.vue'
import ScoreCard from '@/components/ScoreCard.vue'
import LineChart from '@/components/LineChart.vue'
import { useTransactionsStore } from '@/store/transactions_store'
import { computed, ref, watch } from 'vue'
import moment from 'moment'
import {
	breakdown,
	expensesSliceFunc,
	incomeSliceFunc,
	investingSliceFunc,
	miscellaneousSliceFunc,
	homeSliceFunc,
	restaurantsSliceFunc,
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

function isSameYearAsCurrentDate(date: Date, currentDate: Date) {
	return currentDate.getFullYear() === date.getFullYear()
}

function isPreviousYearAsCurrentDate(date: Date) {
	const previousDate = new Date(currentDate.value || new Date())
	previousDate.setFullYear(previousDate.getFullYear() - 1)
	return previousDate.getFullYear() === date.getFullYear()
}
function isNextYearAsCurrentDate(date: Date) {
	const nextDate = new Date(currentDate.value || new Date())
	nextDate.setFullYear(nextDate.getFullYear() + 1)
	return nextDate.getFullYear() === date.getFullYear()
}

const expensesScoreCard = computed(() => {
	return scoreCard(transactions.value, expensesSliceFunc, {
		current: (date) => isSameYearAsCurrentDate(date, currentDate.value || new Date()),
		next: isNextYearAsCurrentDate,
		previous: isPreviousYearAsCurrentDate,
	})
})

const miscellaneousScoreCard = computed(() => {
	return scoreCard(transactions.value, miscellaneousSliceFunc, {
		current: (date) => isSameYearAsCurrentDate(date, currentDate.value || new Date()),
		next: isNextYearAsCurrentDate,
		previous: isPreviousYearAsCurrentDate,
	})
})

const expensesBreakdown = computed(() => {
	const b = breakdown(transactions.value, expensesSliceFunc, (date: Date) =>
		isSameYearAsCurrentDate(date, currentDate.value || new Date())
	)
	return b
})

const miscellaneousBreakdown = computed(() => {
	return breakdown(transactions.value, miscellaneousSliceFunc, (date: Date) =>
		isSameYearAsCurrentDate(date, currentDate.value || new Date())
	)
})

const subtractYear = () => {
	if (currentDate.value) {
		const newDate = new Date(currentDate.value)
		newDate.setFullYear(newDate.getFullYear() - 1)
		currentDate.value = newDate
	}
}

const addYear = () => {
	if (currentDate.value) {
		const newDate = new Date(currentDate.value)
		newDate.setFullYear(newDate.getFullYear() + 1)
		currentDate.value = newDate
	}
}

const incomeExpensesBreakdown = computed(() => {
	const dates = ['Category']
	const income = ['Income'] as (string | number)[]
	const expenses = ['Expenses'] as (string | number)[]
	const home = ['Home'] as (string | number)[]
	const restaurants = ['Restaurants'] as (string | number)[]
	const investing = ['Investing'] as (string | number)[]

	const startDate = new Date(currentDate?.value || new Date())
	startDate.setFullYear(startDate.getFullYear() - 2)
	const endDate = new Date(currentDate?.value || new Date())
	endDate.setFullYear(endDate.getFullYear() + 2)

	while (startDate <= endDate) {
		dates.push(moment(startDate).format('YYYY'))
		income.push(
			totalBreakdownAmount(transactions.value, incomeSliceFunc, (date: Date) =>
				isSameYearAsCurrentDate(date, startDate)
			).toFixed(2)
		)
		expenses.push(
			totalBreakdownAmount(transactions.value, expensesSliceFunc, (date: Date) =>
				isSameYearAsCurrentDate(date, startDate)
			).toFixed(2)
		)
		investing.push(
			totalBreakdownAmount(transactions.value, investingSliceFunc, (date: Date) =>
				isSameYearAsCurrentDate(date, startDate)
			).toFixed(2)
		)
		home.push(
			totalBreakdownAmount(transactions.value, homeSliceFunc, (date: Date) =>
				isSameYearAsCurrentDate(date, startDate)
			).toFixed(2)
		)
		restaurants.push(
			totalBreakdownAmount(transactions.value, restaurantsSliceFunc, (date: Date) =>
				isSameYearAsCurrentDate(date, startDate)
			).toFixed(2)
		)

		startDate.setFullYear(startDate.getFullYear() + 1)
	}

	return [dates, income, expenses, home, restaurants, investing]
})
</script>

<template>
	<div class="container text-center">
		<div class="row align-items-center">
			<div class="col">
				<div class="btn-group" role="group">
					<button type="button" class="btn btn-outline-secondary" @click="subtractYear">
						<i class="bi bi-caret-left"></i>
					</button>
					<button type="button" class="btn btn-outline-secondary month-button">
						{{ $moment(currentDate).format('YYYY') }}
					</button>
					<button type="button" class="btn btn-outline-secondary" @click="addYear">
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
		<PieChart :title="'Miscellaneous'" :data="miscellaneousBreakdown"></PieChart>
	</div>
	<div class="scorecards">
		<ScoreCard
			:title="'Expenses'"
			:current-title="'Current Year'"
			:previous-title="'Previous Year'"
			:next-title="'Next Year'"
			:score-card="expensesScoreCard"
		>
		</ScoreCard>
		<ScoreCard
			:title="'Miscellaneous'"
			:current-title="'Current Year'"
			:previous-title="'Previous Year'"
			:next-title="'Next Year'"
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