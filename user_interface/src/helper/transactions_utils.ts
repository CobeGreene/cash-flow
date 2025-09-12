import { getAmount, getCategory, getDate, getSubCategory } from '@/store/transactions_store'

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

export function grocerySliceFunc(row: string[]): Breakdown {
  if (getCategory(row) === 'Groceries') {
    return { name: getSubCategory(row), value: -1 * getAmount(row) }
  }
  return undefined
}

export function investingSliceFunc(row: string[]): Breakdown {
  if (getCategory(row) === 'Investing' && getSubCategory(row) === 'Charles Schwab') {
    return { name: getSubCategory(row), value: -1 * getAmount(row) }
  }
  return undefined
}

const expensesCategories = new Set([
  'Groceries',
  'Car',
  'Home',
  'Insurance',
  'Medical',
  'Miscellaneous',
  'Travel',
  'Vacation',
])

export function expensesSliceFunc(row: string[]): Breakdown {
  if (expensesCategories.has(getCategory(row))) {
    return { name: getCategory(row), value: -1 * getAmount(row) }
  }
  return undefined
}

export function incomeSliceFunc(row: string[]): Breakdown {
  const category = getCategory(row)
  const subCategory = getSubCategory(row)
  if (getCategory(row) === 'Taxes') {
    return { name: 'Work', value: -1 * getAmount(row) }
  } else if (
    (category === 'Bank' && subCategory === 'Cash Back Rewards') ||
    (category === 'Investing' && subCategory !== 'Charles Schwab') ||
    category === 'Work'
  ) {
    return { name: category, value: getAmount(row) }
  }
  return undefined
}

export function miscellaneousSliceFunc(row: string[]): Breakdown {
  if (getCategory(row) === 'Miscellaneous') {
    return { name: getSubCategory(row), value: -1 * getAmount(row) }
  }
  return undefined
}

export function breakdown(
  transactions: string[][],
  sliceFunc: (row: string[]) => { name: string; value: number } | undefined,
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
  transactions: string[][],
  sliceFunc: (row: string[]) => { name: string; value: number } | undefined,
  isWithinTimeFrame: (date: Date) => boolean,
): number {
  return breakdown(transactions, sliceFunc, isWithinTimeFrame)
    .map((b) => b.value)
    .reduce((acc, value) => acc + value, 0)
}

export function scoreCard(
  transactions: string[][],
  sliceFunc: (row: string[]) => { name: string; value: number } | undefined,
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
