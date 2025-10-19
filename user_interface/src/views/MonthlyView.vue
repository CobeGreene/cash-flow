<script setup lang="ts">
import TimeBasedView from '@/components/TimeBasedView.vue'
import moment from 'moment'

function isSameMonthAsCurrentDate(date: Date, currentDate: Date) {
	return (
		currentDate.getMonth() === date.getMonth() &&
		currentDate.getFullYear() === date.getFullYear()
	)
}

function isPreviousMonthAsCurrentDate(date: Date, currentDate: Date) {
	const previousDate = new Date(currentDate)
	previousDate.setMonth(previousDate.getMonth() - 1)
	return (
		previousDate.getMonth() === date.getMonth() &&
		previousDate.getFullYear() === date.getFullYear()
	)
}
function isNextMonthAsCurrentDate(date: Date, currentDate: Date) {
	const nextDate = new Date(currentDate)
	nextDate.setMonth(nextDate.getMonth() + 1)
	return nextDate.getMonth() === date.getMonth() && nextDate.getFullYear() === date.getFullYear()
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
		:isPreviousTimeAsCurrentDate="isPreviousMonthAsCurrentDate"
		:isNextTimeAsCurrentDate="isNextMonthAsCurrentDate"
		:getNextTime="getNextMonth"
		:getPreviousTime="getPreviousMonth"
		:getFormatTime="getFormatMonth"
		:timeUnit="'Month'"
	/>
</template>