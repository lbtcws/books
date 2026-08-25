import { defineStore } from 'pinia'

const STORAGE_KEY = 'books-reader-progress'

function load() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}
  } catch {
    return {}
  }
}

// 阅读进度：按书籍 id 记忆页码，持久化到 localStorage
export const useProgressStore = defineStore('progress', {
  state: () => ({
    data: load(),
  }),
  actions: {
    setProgress(bookId, { page, total }) {
      this.data[bookId] = { page, total, updatedAt: Date.now() }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.data))
    },
    getProgress(bookId) {
      return this.data[bookId] || null
    },
  },
})
