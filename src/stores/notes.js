import { defineStore } from 'pinia'

const STORAGE_KEY = 'books-reader-notes'

function load() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}
  } catch {
    return {}
  }
}

// 本地笔记：按书籍 id 保存笔记条目，持久化到 localStorage
export const useNotesStore = defineStore('notes', {
  state: () => ({
    data: load(),
  }),
  getters: {
    byBook: (state) => (bookId) => state.data[bookId] || [],
  },
  actions: {
    add(bookId, { text, location }) {
      const list = this.data[bookId] || []
      list.unshift({ id: `${Date.now()}`, time: Date.now(), text, location: location || null })
      this.data[bookId] = list
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.data))
    },
    remove(bookId, id) {
      this.data[bookId] = (this.data[bookId] || []).filter((n) => n.id !== id)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.data))
    },
  },
})
