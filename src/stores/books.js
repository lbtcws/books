import { defineStore } from 'pinia'
import { books, booksByCategory, categoryIcons } from '../data/books'

export const useBooksStore = defineStore('books', {
  state: () => ({
    list: books,
    byCategory: booksByCategory,
    categoryIcons,
  }),
  getters: {
    byId: (state) => (id) => state.list.find((b) => b.id === id),
    totalBooks: (state) => state.list.length,
    totalCategories: (state) => Object.keys(state.byCategory).length,
  },
})
