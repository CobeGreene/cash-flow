import {
  getAmount,
  getCategory,
  getDate,
  getSubCategory,
  type Transaction,
} from '@/store/transactions_store'

export interface BreakdownType {
  name: string
  value: number
}

export type Breakdown = BreakdownType | undefined

export type isWithinTimeFrame = (date: Date) => boolean

export interface ScoreCardTimeFrameFunctions {
  next: isWithinTimeFrame
  previous: isWithinTimeFrame
  current: isWithinTimeFrame
}

export interface ScoreCard {
  previous: number
  next: number
  current: number
  percentageIncreaseFromNext: number | undefined
  percentageIncreaseFromPrevious: number | undefined
}

export function createSliceFunc(
  category: string | null,
  subCategory: string | null,
  invertAmount = true,
): (row: Transaction) => Breakdown {
  return (row: Transaction): Breakdown => {
    if (
      (category === null || getCategory(row) === category) &&
      (subCategory === null || getSubCategory(row) === subCategory)
    ) {
      const amount = getAmount(row)
      return {
        name: getSubCategory(row),
        value: invertAmount ? -1 * amount : amount,
      }
    }
  }
}

export const investingSliceFunc = createSliceFunc('Investment', null, true)

const nonExpensesCategories = new Set(['Investment', 'Income', 'Ignore'])

export function expensesSliceFunc(row: Transaction): Breakdown {
  if (nonExpensesCategories.has(getCategory(row))) {
    return undefined
  }
  return { name: getCategory(row), value: -1 * getAmount(row) }
}

export const incomeSliceFunc = createSliceFunc('Income', null, false)

export const miscellaneousSliceFunc = createSliceFunc('Miscellaneous', null, true)

export function breakdown(
  transactions: Transaction[],
  sliceFunc: (row: Transaction) => { name: string; value: number } | undefined,
  isWithinTimeFrame: (date: Date) => boolean,
): { name: string; value: number }[] {
  const data: { [key: string]: { value: number; name: string } } = {}

  for (const row of transactions) {
    if (!isWithinTimeFrame(getDate(row))) {
      continue
    }
    const slice = sliceFunc(row)
    if (slice) {
      data[slice.name] = data[slice.name] || { name: slice.name, value: 0 }
      data[slice.name].value += slice.value
    }
  }
  return Object.values(data)
}

export function totalBreakdownAmount(
  transactions: Transaction[],
  sliceFunc: (row: Transaction) => { name: string; value: number } | undefined,
  isWithinTimeFrame: (date: Date) => boolean,
): number {
  return breakdown(transactions, sliceFunc, isWithinTimeFrame)
    .map((b) => b.value)
    .reduce((acc, value) => acc + value, 0)
}

export function scoreCard(
  transactions: Transaction[],
  sliceFunc: (row: Transaction) => { name: string; value: number } | undefined,
  timeFrameFunctions: ScoreCardTimeFrameFunctions,
): ScoreCard {
  const previous = totalBreakdownAmount(transactions, sliceFunc, timeFrameFunctions.previous)
  const current = totalBreakdownAmount(transactions, sliceFunc, timeFrameFunctions.current)
  const next = totalBreakdownAmount(transactions, sliceFunc, timeFrameFunctions.next)

  return {
    previous,
    current,
    next,
    percentageIncreaseFromNext: next == 0 ? undefined : (current - next) / next,
    percentageIncreaseFromPrevious: previous == 0 ? undefined : (current - previous) / previous,
  }
}
