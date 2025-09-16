import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

type Transaction = (string | number | Date)[]

// Transaction is row with the following data in this format
// 0: Date
// 2: Name
// 4: Amount
// 5: Category
// 6: Sub-Category
export function getDate(row: Transaction): Date {
  return row[0] as Date
}

export function getName(row: Transaction): string {
  return row[2] as string
}

export function getAmount(row: Transaction): number {
  return row[4] as number
}

export function getCategory(row: Transaction): string {
  return row[5] as string
}

export function getSubCategory(row: Transaction): string {
  return row[6] as string
}

export const useTransactionsStore = defineStore('transactions', () => {
  const transactions = ref<Transaction[]>([])

  function loadTransactions(data: Transaction[]) {
    const formattedData: Transaction[] = data.map((row) => {
      row[0] = new Date(row[0]) // Date
      row[4] = Number(row[4]) // Amount
      return row
    })
    transactions.value = formattedData
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
