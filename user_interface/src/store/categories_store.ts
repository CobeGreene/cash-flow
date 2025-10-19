import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

type EditChange =
  | { subCategory: string; newName: string | null } // update
  | { subCategory: string } // delete
  | { subCategory: string | null; category: string } // add

export const useCategoriesStore = defineStore('categories', () => {
  const categories = ref<{ [key: string]: string[] }>({})

  const allCategories = computed(() => {
    return Object.keys(categories.value).sort()
  })

  const allSubCategories = computed(() => {
    const subs: string[] = []
    for (const key in categories.value) {
      subs.push(...categories.value[key])
    }
    return subs.sort()
  })

  const editCategories = ref<{ [key: string]: string[] }>({})
  const editChanges = ref<{ type: string; change: EditChange }[]>([])
  const incomeEditSubCategories = computed(() => editCategories.value['Income'] || [])
  const ignoreEditSubCategories = computed(() => editCategories.value['Ignore'] || [])
  const investmentEditSubCategories = computed(() => editCategories.value['Investment'] || [])

  const expensesEditCategories = computed(() => {
    return Object.fromEntries(
      Object.entries(editCategories.value).filter(
        ([key]) => key !== 'Income' && key !== 'Ignore' && key !== 'Investment',
      ),
    )
  })

  function restoreEditCategories() {
    const categoriesCopy: { [key: string]: string[] } = {}
    for (const key in categories.value) {
      categoriesCopy[key] = [...categories.value[key]]
    }
    editCategories.value = categoriesCopy
    editChanges.value = []
  }

  function loadCategories(data: { [key: string]: string[] }) {
    categories.value = data
    restoreEditCategories()
  }

  function updateCategory(oldName: string, newName: string | null) {
    if (oldName === newName) {
      return
    }
    const newCategories: { [key: string]: string[] } = {}
    for (const key in editCategories.value) {
      if (newName === null) {
        newCategories[key] = editCategories.value[key].filter((cat) => cat !== oldName)
        continue
      } else {
        newCategories[key] = editCategories.value[key].map((cat) =>
          cat === oldName ? newName : cat,
        )
      }
    }
    editCategories.value = newCategories
    if (newName === null) {
      editChanges.value.push({ type: 'delete', change: { subCategory: oldName } })
    } else {
      editChanges.value.push({ type: 'update', change: { subCategory: oldName, newName } })
    }
  }

  function addSubCategory(category: string, subCategory: string | null) {
    const newCategories: { [key: string]: string[] } = {}
    for (const key in editCategories.value) {
      newCategories[key] = [...editCategories.value[key]]
    }
    newCategories[category] = newCategories[category] || []
    if (subCategory !== null) {
      newCategories[category].push(subCategory)
    }
    editCategories.value = newCategories
    editChanges.value.push({ type: 'add', change: { subCategory, category } })
  }

  function getCategoryOfSubCategory(subCategory: string): string | null {
    for (const key in categories.value) {
      if (categories.value[key].includes(subCategory)) {
        return key
      }
    }
    return null
  }

  return {
    categories,
    allCategories,
    allSubCategories,
    loadCategories,
    updateCategory,
    addSubCategory,
    incomeEditSubCategories,
    ignoreEditSubCategories,
    investmentEditSubCategories,
    expensesEditCategories,
    restoreEditCategories,
    getCategoryOfSubCategory,
    editChanges,
  }
})
