<script setup lang="ts">
import TimeBasedView from '@/components/TimeBasedView.vue'
import moment from 'moment'
import { useTransactionsStore } from '@/store/transactions_store'
import { storeToRefs } from 'pinia'

const store = useTransactionsStore()
const { maxDate } = storeToRefs(store)

function isSameYearAsCurrentDate(date: Date, currentDate: Date) {
	return currentDate.getFullYear() === date.getFullYear()
}

function isSameYearAsCurrentYtd(date: Date, currentDate: Date) {
	if (!maxDate.value) {
		return isSameYearAsCurrentDate(date, currentDate)
	}
	if (!isSameYearAsCurrentDate(date, currentDate)) {
		return false
	}
	if (date.getMonth() > maxDate.value?.getMonth()) {
		return false
	}
	if (date.getMonth() < maxDate.value?.getMonth()) {
		return true
	}
	return date.getDate() <= maxDate.value?.getDate()
}

function getNextYear(date: Date): Date {
	const nextDate = new Date(date)
	nextDate.setFullYear(nextDate.getFullYear() + 1)
	return nextDate
}

function getPreviousYear(date: Date): Date {
	const previousDate = new Date(date)
	previousDate.setFullYear(previousDate.getFullYear() - 1)
	return previousDate
}

function getFormatYear(date: Date): string {
	return moment(date).format('YYYY')
}
</script>

<template>
	<TimeBasedView
		:isSameTimeAsCurrentDate="isSameYearAsCurrentDate"
		:isSameTimeAsCurrentYtd="isSameYearAsCurrentYtd"
		:getNextTime="getNextYear"
		:getPreviousTime="getPreviousYear"
		:getFormatTime="getFormatYear"
		:timeUnit="'Year'"
	/>
</template>