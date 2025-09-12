<script setup lang="ts">
import { type ScoreCard } from '@/helper/transactions_utils'

const props = defineProps<{
	scoreCard: ScoreCard
	title: string
	currentTitle: string
	previousTitle: string
	nextTitle: string
}>()
</script>

<template>
	<div class="card financial-card rounded-4 shadow-sm">
		<div class="card-header">
			<h2 class="text-center">{{ props.title }}</h2>
		</div>
		<div class="card-body p4">
			<div class="mb-4">
				<p class="text-secondary text-uppercase fs-6 mb-1">{{ props.currentTitle }}</p>
				<div class="d-flex align-items-center justify-content-between">
					<span class="fw-bold fs-2 text-dark"
						>${{ props.scoreCard.current.toFixed(2) }}</span
					>
				</div>
			</div>

			<div class="row g-2 text-center">
				<div class="col-6">
					<div class="bg-light p-3 rounded-3">
						<p class="text-secondary text-uppercase fs-6 mb-1">
							{{ props.previousTitle }}
						</p>
						<div class="d-flex flex-column align-items-center">
							<span class="fs-5 fw-semibold text-dark"
								>${{ props.scoreCard.previous.toFixed(2) }}</span
							>
							<div
								class="d-flex align-items-center fw-medium mt-1"
								:class="{
									'text-success':
										props.scoreCard.percentageIncreaseFromPrevious || 0 < 0,
									'text-danger':
										props.scoreCard.percentageIncreaseFromPrevious || 0 > 0,
								}"
							>
								<i
									v-if="props.scoreCard.percentageIncreaseFromPrevious || 0 > 0"
									class="bi bi-arrow-down"
								></i>
								<i
									v-if="props.scoreCard.percentageIncreaseFromPrevious || 0 < 0"
									class="bi bi-arrow-down"
								></i>
								<span
									>${{
										(
											(props.scoreCard.percentageIncreaseFromPrevious || 0) *
											100
										).toFixed(2)
									}}%</span
								>
							</div>
						</div>
					</div>
				</div>
				<div class="col-6">
					<div class="bg-light p-3 rounded-3">
						<p class="text-secondary text-uppercase fs-6 mb-1">{{ props.nextTitle }}</p>
						<div class="d-flex flex-column align-items-center">
							<span class="fs-5 fw-semibold text-dark"
								>${{ props.scoreCard.next.toFixed(2) }}</span
							>
							<div
								class="d-flex align-items-center fw-medium mt-1"
								:class="{
									'text-success':
										props.scoreCard.percentageIncreaseFromNext || 0 < 0,
									'text-danger':
										props.scoreCard?.percentageIncreaseFromNext || 0 > 0,
								}"
							>
								<i
									v-if="props.scoreCard.percentageIncreaseFromNext || 0 > 0"
									class="bi bi-arrow-down"
								></i>
								<i
									v-if="props.scoreCard.percentageIncreaseFromNext || 0 < 0"
									class="bi bi-arrow-down"
								></i>
								<span
									>${{
										(
											(props.scoreCard.percentageIncreaseFromNext || 0) * 100
										).toFixed(2)
									}}%</span
								>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>
.financial-card {
	transition: all 0.3s ease-in-out;
}
.financial-card:hover {
	transform: scale(1.02);
	box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
</style>