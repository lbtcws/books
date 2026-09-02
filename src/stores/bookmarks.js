import { defineStore } from 'pinia'

const STORAGE_KEY = 'books-reader-bookmarks'

function load() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}
  } catch {
    return {}
  }
}

// 书签：按书籍 id 保存位置（epub 为 CFI，pdf 为页码），持久化到 localStorage
export const useBookmarksStore = defineStore('bookmarks', {
  state: () => ({
    data: load(),
  }),
  getters: {
    byBook: (state) => (bookId) => state.data[bookId] || [],
  },
  actions: {
    add(bookId, bookmark) {
      const list = this.data[bookId] || []
      list.unshift({ id: `${Date.now()}`, time: Date.now(), ...bookmark })
      this.data[bookId] = list
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.data))
    },
    remove(bookId, id) {
      this.data[bookId] = (this.data[bookId] || []).filter((b) => b.id !== id)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.data))
    },
  },
})
