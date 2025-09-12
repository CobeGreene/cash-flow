<script setup lang="ts">
import {
	useTransactionsStore,
	getDate,
	getName,
	getAmount,
	getCategory,
	getSubCategory,
} from '@/store/transactions_store'
import { storeToRefs } from 'pinia'

const store = useTransactionsStore()

const { transactions } = storeToRefs(store)
</script>

<template>
	<h1>Raw</h1>
	<table class="table table-striped">
		<thead class="thead-dark">
			<tr>
				<th scope="col">#</th>
				<th scope="col">Date</th>
				<th scope="col">Name</th>
				<th scope="col">Amount</th>
				<th scope="col">Category</th>
				<th scope="col">Sub-Category</th>
			</tr>
		</thead>
		<tbody>
			<tr v-for="(item, index) in transactions">
				<th scope="row">{{ index + 1 }}</th>
				<td>{{ $moment(getDate(item)).format('YYYY-MM-DD') }}</td>
				<td>{{ getName(item) }}</td>
				<td>{{ getAmount(item) }}</td>
				<td>{{ getCategory(item) }}</td>
				<td>{{ getSubCategory(item) }}</td>
			</tr>
		</tbody>
	</table>
</template>