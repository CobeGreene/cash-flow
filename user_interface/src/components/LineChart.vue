<script setup lang="ts">
import { use } from 'echarts/core'
import { LineChart, PieChart } from 'echarts/charts'
import {
	GridComponent,
	DatasetComponent,
	LegendComponent,
	TooltipComponent,
	ToolboxComponent,
} from 'echarts/components'
import { shallowRef, computed } from 'vue'
import VChart from 'vue-echarts'

use([
	DatasetComponent,
	GridComponent,
	LegendComponent,
	LineChart,
	TooltipComponent,
	ToolboxComponent,
	PieChart,
])

const props = defineProps<{
	data: (string | number)[][]
}>()

const option = computed(() => ({
	textStyle: {
		fontFamily: 'Inter, "Helvetica Neue", Arial, sans-serif',
		fontWeight: 300,
	},
	legend: { top: 20 },
	tooltip: {
		trigger: 'axis',
	},
	dataset: {
		source: props.data,
	},
	xAxis: {
		type: 'category',
		triggerEvent: true,
		tooltip: { show: true, formatter: '' },
	},
	yAxis: {
		triggerEvent: true,
		tooltip: { show: true, formatter: '' },
	},
	series: [
		{
			type: 'line',
			smooth: true,
			seriesLayoutBy: 'row',
			emphasis: { focus: 'series' },
		},
		{
			type: 'line',
			smooth: true,
			seriesLayoutBy: 'row',
			emphasis: { focus: 'series' },
		},
		{
			type: 'line',
			smooth: true,
			seriesLayoutBy: 'row',
			emphasis: { focus: 'series' },
		},
	],
}))

const axis = shallowRef('xAxis')
</script>

<template>
	<v-chart :option="option" autoresize>
		<template #[`tooltip-${axis}`]="params">
			{{ axis === 'xAxis' ? 'Year' : 'Value' }}:
			<b>{{ params.name }}</b>
		</template>
		<template #dataView="option">
			<table style="margin: 20px auto">
				<thead>
					<tr>
						<th v-for="(t, i) in option.dataset[0].source[0]" :key="i">
							{{ t }}
						</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="(row, i) in option.dataset[0].source.slice(1)" :key="i">
						<th>{{ row[0] }}</th>
						<td v-for="(v, i) in row.slice(1)" :key="i">{{ v }}</td>
					</tr>
				</tbody>
			</table>
		</template>
	</v-chart>
</template>

<style scoped>
th,
td {
	padding: 4px 8px;
}
</style>