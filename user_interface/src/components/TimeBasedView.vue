<script lang="ts" setup>
import { storeToRefs } from 'pinia'
import PieChart from '@/components/PieChart.vue'
import TableBreakdown from '@/components/TableBreakdown.vue'
import ScoreCard from '@/components/ScoreCard.vue'
import LineChart from '@/components/LineChart.vue'
import { useTransactionsStore } from '@/store/transactions_store'
import { useCategoriesStore } from '@/store/categories_store'
import { computed, ref, watch } from 'vue'
import {
	breakdown,
	expensesSliceFunc,
	incomeSliceFunc,
	miscellaneousSliceFunc,
	scoreCard,
	totalBreakdownAmount,
	createSliceFunc,
} from '@/helper/transactions_utils'

const store = useTransactionsStore()
const categoriesStore = useCategoriesStore()
const { transactions, maxDate, hasData } = storeToRefs(store)
const { allCategories } = storeToRefs(categoriesStore)
const currentDate = ref<Date>(new Date())
const selectedCategories = ref<string[]>(['Income', 'Expenses', 'Investment'])
const categoriesToSelect = computed(() => {
	return [...allCategories.value.filter((x) => x !== 'Ignore'), 'Expenses']
})

type TimeFunction = (date: Date, currentDate: Date) => boolean

const props = defineProps<{
	isSameTimeAsCurrentDate: TimeFunction
	isPreviousTimeAsCurrentDate: TimeFunction
	isNextTimeAsCurrentDate: TimeFunction
	getNextTime: (date: Date) => Date
	getPreviousTime: (date: Date) => Date
	getFormatTime: (date: Date) => string
	timeUnit: string
}>()

currentDate.value = maxDate.value || new Date()

watch(hasData, (_value, _oldValue) => {
	currentDate.value = maxDate.value || new Date()
})

const expensesScoreCard = computed(() => {
	return scoreCard(transactions.value, expensesSliceFunc, {
		current: (date) => props.isSameTimeAsCurrentDate(date, currentDate.value),
		next: (date) => props.isNextTimeAsCurrentDate(date, currentDate.value),
		previous: (date) => props.isPreviousTimeAsCurrentDate(date, currentDate.value),
	})
})

const miscellaneousScoreCard = computed(() => {
	return scoreCard(transactions.value, miscellaneousSliceFunc, {
		current: (date) => props.isSameTimeAsCurrentDate(date, currentDate.value),
		next: (date) => props.isNextTimeAsCurrentDate(date, currentDate.value),
		previous: (date) => props.isPreviousTimeAsCurrentDate(date, currentDate.value),
	})
})

const expensesBreakdown = computed(() => {
	const b = breakdown(transactions.value, expensesSliceFunc, (date: Date) =>
		props.isSameTimeAsCurrentDate(date, currentDate.value)
	)
	return b
})

const miscellaneousBreakdown = computed(() => {
	return breakdown(transactions.value, miscellaneousSliceFunc, (date: Date) =>
		props.isSameTimeAsCurrentDate(date, currentDate.value)
	)
})

const subtractTime = () => {
	if (currentDate.value) {
		currentDate.value = props.getPreviousTime(currentDate.value)
	}
}

const addTime = () => {
	if (currentDate.value) {
		currentDate.value = props.getNextTime(currentDate.value)
	}
}

function addLineCategory() {
	selectedCategories.value = [...selectedCategories.value, categoriesToSelect.value[0]]
}

const incomeExpensesBreakdown = computed(() => {
	const result = [] as (string | number)[][]
	result.push(['Category'])
	for (const category of selectedCategories.value) {
		result.push([category])
	}

	let startDate = props.getPreviousTime(props.getPreviousTime(currentDate.value))
	const endDate = props.getNextTime(props.getNextTime(currentDate.value))

	while (startDate <= endDate) {
		result[0].push(props.getFormatTime(startDate))
		for (let i = 0; i < selectedCategories.value.length; ++i) {
			const category = selectedCategories.value[i]
			let sliceFunc = createSliceFunc(category, null, true)
			if (category === 'Income') {
				sliceFunc = incomeSliceFunc
			} else if (category === 'Expenses') {
				sliceFunc = expensesSliceFunc
			}
			result[i + 1].push(
				totalBreakdownAmount(transactions.value, sliceFunc, (date: Date) =>
					props.isSameTimeAsCurrentDate(date, startDate)
				).toFixed(2)
			)
		}
		startDate = props.getNextTime(startDate)
	}

	return result
})
</script>

<template>
	<div class="container text-center">
		<div class="row align-items-center">
			<div class="col">
				<div class="btn-group" role="group">
					<button type="button" class="btn btn-outline-secondary" @click="subtractTime">
						<i class="bi bi-caret-left"></i>
					</button>
					<button type="button" class="btn btn-outline-secondary month-button">
						{{ props.getFormatTime(currentDate) }}
					</button>
					<button type="button" class="btn btn-outline-secondary" @click="addTime">
						<i class="bi bi-caret-right"></i>
					</button>
				</div>
			</div>
		</div>
	</div>
	<div class="container d-flex mt-5">
		<select
			class="form-select category-select"
			v-for="(selectedCategory, index) in selectedCategories"
			v-model="selectedCategories[index]"
			:key="index"
		>
			<option
				v-for="category in categoriesToSelect"
				:key="category"
				:value="category"
				:selected="category === selectedCategory"
			>
				{{ category }}
			</option>
		</select>
		<button class="btn btn-outline-secondary" type="button" @click="addLineCategory">
			Add Category
		</button>
	</div>
	<div class="income-charts">
		<LineChart :data="incomeExpensesBreakdown" :time-unit="props.timeUnit"></LineChart>
	</div>
	<div class="breakdown-table">
		<TableBreakdown
			:current-date="currentDate"
			:time-unit="props.timeUnit"
			:get-next-time="props.getNextTime"
			:get-format-time="props.getFormatTime"
			:get-previous-time="props.getPreviousTime"
			:is-same-time-as-current-date="props.isSameTimeAsCurrentDate"
		>
		</TableBreakdown>
	</div>
	<!-- <div class="charts">
		<PieChart :title="'Expenses'" :data="expensesBreakdown"></PieChart>
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
			:title="'Miscellaneous'"
			:current-title="'Current Month'"
			:previous-title="'Previous Month'"
			:next-title="'Next Month'"
			:score-card="miscellaneousScoreCard"
		>
		</ScoreCard>
	</div> -->
</template>

<style scoped>
.income-charts {
	display: grid;
	grid-template-columns: 1fr;
	grid-template-rows: 300px;
}

.category-select {
	max-width: fit-content;
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