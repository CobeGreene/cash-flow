import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

// Transaction is row with the following data in this format
// 0: Date
// 2: Name
// 4: Amount
// 5: Category
// 6: Sub-Category
export function getDate(row: string[]) {
  return new Date(row[0])
}

export function getName(row: string[]) {
  return row[2]
}

export function getAmount(row: string[]) {
  return Number(row[4])
}

export function getCategory(row: string[]) {
  return row[5]
}

export function getSubCategory(row: string[]) {
  return row[6]
}

export const useTransactionsStore = defineStore('transactions', () => {
  const transactions = ref<string[][]>([])

  function loadTransactions(data: string[][]) {
    transactions.value = data
  }

  const hasData = computed(() => transactions.value.length !== 0)

  const maxDate = computed(() =>
    hasData.value
      ? new Date(Math.max(...transactions.value.map((row) => getDate(row).getTime())))
      : undefined,
  )

  const minDate = computed(() =>
    hasData.value
      ? new Date(Math.min(...transactions.value.map((row) => getDate(row).getTime())))
      : undefined,
  )

  return { transactions, loadTransactions, maxDate, minDate, hasData }
})
