<script setup lang="ts">
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { computed } from 'vue'

use([CanvasRenderer, PieChart, TitleComponent, TooltipComponent, LegendComponent])

const props = defineProps<{
	title?: string
	data: { value: number; name: string }[]
}>()

const option = computed(() => ({
	title: props.title
		? {
				text: props.title,
				left: 'center',
				padding: [0, 0, 20, 0],
		  }
		: {},
	tooltip: {
		trigger: 'item',
		formatter: '{b}: {d}%',
	},
	series: [
		{
			name: 'Sources',
			type: 'pie',
			radius: '60%',
			center: ['50%', '50%'],
			data: props.data,
			emphasis: {
				itemStyle: {
					shadowBlur: 10,
					shadowOffsetX: 0,
					shadowColor: 'rgba(0, 0, 0, 0.5)',
				},
			},
		},
	],
}))
</script>

<template>
	<VChart :option="option" :autoresize="true"></VChart>
</template>