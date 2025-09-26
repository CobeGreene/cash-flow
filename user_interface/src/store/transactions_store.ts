import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export type Transaction = (string | number | Date)[]

// Transaction is row with the following data in this format
// 0: Date (Original)
// 1: Transaction
// 2: Name
// 3: Memo
// 4: Amount (Original)
// 5: Category
// 6: Sub-Category
// 7: Date (Converted to Date object)
// 8: Amount (Converted to Number)
export function getDate(row: Transaction): Date {
  return row[7] as Date
}

export function getTransaction(row: Transaction): string {
  return row[1] as string
}

export function getName(row: Transaction): string {
  return row[2] as string
}

export function getMemo(row: Transaction): string {
  return row[3] as string
}

export function getAmount(row: Transaction): number {
  return row[8] as number
}

export function getCategory(row: Transaction): string {
  return row[5] as string
}

export function getSubCategory(row: Transaction): string {
  return row[6] as string
}

export function getOriginalDate(row: Transaction): string {
  return row[0] as string
}

export function getOriginalAmount(row: Transaction): string {
  return row[4] as string
}

export const useTransactionsStore = defineStore('transactions', () => {
  const transactions = ref<Transaction[]>([])

  function loadTransactions(data: Transaction[]) {
    const formattedData: Transaction[] = data.map((row) => {
      row.push(new Date(row[0])) // Date
      row.push(Number(row[4])) // Amount
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
