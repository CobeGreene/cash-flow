<script setup lang="ts">
import { ref, inject } from 'vue'
import { RouterView } from 'vue-router'
import { HttpService } from '@/service/http-service'
import { useTransactionsStore } from '@/store/transactions_store'
import { useCategoriesStore } from '@/store/categories_store'

const fileInput = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)

const http = inject<HttpService>('http')
const transactionStore = useTransactionsStore()
const categoriesStore = useCategoriesStore()

http?.get('transactions').then((data) => {
	transactionStore.loadTransactions(data['data'])
})

http?.get('categories').then((data) => {
	categoriesStore.loadCategories(data['data'])
})

const handleFileUpload = async (event: Event) => {
	const target = event.target as HTMLInputElement
	const file = target.files?.[0]

	if (!file) return

	// Check if file is CSV
	if (!file.name.toLowerCase().endsWith('.csv')) {
		alert('Please select a CSV file')
		return
	}

	isUploading.value = true

	try {
		const formData = new FormData()
		formData.append('file', file)

		const response = await fetch('http://127.0.0.1:5000/upload', {
			method: 'POST',
			body: formData,
		})

		if (response.ok) {
			alert('File uploaded successfully!')
		} else {
			throw new Error(`Upload failed: ${response.status}`)
		}
	} catch (error) {
		console.error('Upload error:', error)
		alert('Failed to upload file. Please try again.')
	} finally {
		isUploading.value = false
		// Reset file input
		if (fileInput.value) {
			fileInput.value.value = ''
		}
	}
}

const triggerFileUpload = () => {
	fileInput.value?.click()
}
</script>

<template>
	<div id="app">
		<!-- Bootstrap Navbar -->
		<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
			<div class="container">
				<a class="navbar-brand" href="#">Cash Flow</a>

				<div class="navbar-nav ms-auto">
					<button
						class="btn btn-outline-light"
						@click="triggerFileUpload"
						:disabled="isUploading"
					>
						<span
							v-if="isUploading"
							class="spinner-border spinner-border-sm me-1"
							role="status"
						></span>
						{{ isUploading ? 'Uploading...' : 'Upload CSV' }}
					</button>
				</div>
			</div>
		</nav>

		<!-- Hidden file input -->
		<input
			ref="fileInput"
			type="file"
			accept=".csv"
			@change="handleFileUpload"
			style="display: none"
		/>

		<!-- Main Content -->
		<div class="container mt-4">
			<div class="row">
				<div class="col-12">
					<RouterView />
				</div>
			</div>
		</div>

		<!-- Fixed Button Group at Bottom -->
		<div class="btn-group cash-flow-navbar" role="group">
			<button
				type="button"
				@click="$router.push({ name: 'monthly' })"
				class="btn"
				:class="{
					'btn-primary': $route.name === 'monthly',
					'btn-light': $route.name !== 'monthly',
				}"
			>
				Monthly
			</button>
			<button
				type="button"
				@click="$router.push({ name: 'yearly' })"
				class="btn"
				:class="{
					'btn-primary': $route.name === 'yearly',
					'btn-light': $route.name !== 'yearly',
				}"
			>
				Yearly
			</button>
			<button
				type="button"
				@click="$router.push({ name: 'raw' })"
				class="btn"
				:class="{
					'btn-primary': $route.name === 'raw',
					'btn-light': $route.name !== 'raw',
				}"
			>
				Raw
			</button>
		</div>
	</div>
</template>

<style scoped>
#app {
	min-height: 100vh;
	padding-bottom: 80px; /* Add padding to prevent content from being hidden behind fixed button group */
}

.cash-flow-navbar {
	position: fixed;
	bottom: 20px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 1000;
}
</style>
