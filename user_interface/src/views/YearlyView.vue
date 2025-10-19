<script setup lang="ts">
import TimeBasedView from '@/components/TimeBasedView.vue'
import moment from 'moment'

function isSameYearAsCurrentDate(date: Date, currentDate: Date) {
	return currentDate.getFullYear() === date.getFullYear()
}

function isPreviousYearAsCurrentDate(date: Date, currentDate: Date) {
	const previousDate = new Date(currentDate)
	previousDate.setFullYear(previousDate.getFullYear() - 1)
	return previousDate.getFullYear() === date.getFullYear()
}
function isNextYearAsCurrentDate(date: Date, currentDate: Date) {
	const nextDate = new Date(currentDate)
	nextDate.setFullYear(nextDate.getFullYear() + 1)
	return nextDate.getFullYear() === date.getFullYear()
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
		:isPreviousTimeAsCurrentDate="isPreviousYearAsCurrentDate"
		:isNextTimeAsCurrentDate="isNextYearAsCurrentDate"
		:getNextTime="getNextYear"
		:getPreviousTime="getPreviousYear"
		:getFormatTime="getFormatYear"
		:timeUnit="'Year'"
	/>
</template>