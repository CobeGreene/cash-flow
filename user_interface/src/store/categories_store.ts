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

  function updateCategory(oldName: string, newName: string | null) {
    if (oldName === newName) {
      return
    }
    const newCategories: { [key: string]: string[] } = {}
    for (const key in categories.value) {
      if (newName === null) {
        newCategories[key] = categories.value[key].filter((cat) => cat !== oldName)
        continue
      } else {
        newCategories[key] = categories.value[key].map((cat) => (cat === oldName ? newName : cat))
      }
    }
    categories.value = newCategories
  }

  function addSubCategory(category: string, subCategory: string) {
    const newCategories: { [key: string]: string[] } = {}
    for (const key in categories.value) {
      newCategories[key] = [...categories.value[key]]
    }
    newCategories[category].push(subCategory)
    categories.value = newCategories
  }

  return {
    categories,
    loadCategories,
    updateCategory,
    addSubCategory,
    incomeSubCategories,
    ignoreSubCategories,
    investmentSubCategories,
    expensesCategories,
  }
})
