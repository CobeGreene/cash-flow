import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useCategoriesStore = defineStore('categories', () => {
  const categories = ref<{ [key: string]: string[] }>({})

  const incomeSubCategories = computed(() => categories.value['Income'] || [])
  const ignoreSubCategories = computed(() => categories.value['Ignore'] || [])
  const investmentSubCategories = computed(() => categories.value['Investment'] || [])

  const expensesCategories = computed(() => {
    return Object.fromEntries(
      Object.entries(categories.value).filter(
        ([key]) => key !== 'Income' && key !== 'Ignore' && key !== 'Investment',
      ),
    )
  })

  function loadCategories(data: { [key: string]: string[] }) {
    categories.value = data
  }

  return {
    categories,
    loadCategories,
    incomeSubCategories,
    ignoreSubCategories,
    investmentSubCategories,
    expensesCategories,
  }
})
