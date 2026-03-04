<script setup lang="ts">
import TimeBasedView from '@/components/TimeBasedView.vue'
import moment from 'moment'
import { useTransactionsStore } from '@/store/transactions_store'
import { storeToRefs } from 'pinia'

const store = useTransactionsStore()
const { maxDate } = storeToRefs(store)

function isSameMonthAsCurrentDate(date: Date, currentDate: Date) {
	return (
		currentDate.getMonth() === date.getMonth() &&
		currentDate.getFullYear() === date.getFullYear()
	)
}

function isSameMonthAsCurrentMtd(date: Date, currentDate: Date) {
	if (!maxDate.value) {
		return isSameMonthAsCurrentDate(date, currentDate)
	}
	return isSameMonthAsCurrentDate(date, currentDate) && date.getDay() <= maxDate.value?.getDay()
}

function getNextMonth(date: Date): Date {
	const nextDate = new Date(date)
	nextDate.setMonth(nextDate.getMonth() + 1)
	return nextDate
}

function getPreviousMonth(date: Date): Date {
	const previousDate = new Date(date)
	previousDate.setMonth(previousDate.getMonth() - 1)
	return previousDate
}

function getFormatMonth(date: Date): string {
	return moment(date).format('MMMM YYYY')
}
</script>

<template>
	<TimeBasedView
		:isSameTimeAsCurrentDate="isSameMonthAsCurrentDate"
		:isSameTimeAsCurrentYtd="isSameMonthAsCurrentMtd"
		:getNextTime="getNextMonth"
		:getPreviousTime="getPreviousMonth"
		:getFormatTime="getFormatMonth"
		:timeUnit="'Month'"
	/>
</template>