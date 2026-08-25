<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import { useBooksStore } from './stores/books'

const route = useRoute()
const store = useBooksStore()
const isReader = computed(() => route.name === 'reader')
</script>

<template>
  <div class="flex min-h-full flex-col">
    <header
      class="sticky top-0 z-20 h-14 shrink-0 border-b border-slate-200 bg-white/80 backdrop-blur"
    >
      <div class="mx-auto flex h-full max-w-5xl items-center gap-2 px-4">
        <span class="text-2xl">📚</span>
        <router-link
          to="/"
          class="text-lg font-semibold text-slate-800 transition hover:text-indigo-600"
        >
          码外人生
        </router-link>
        <div class="flex-1" />
        <div v-if="!isReader" class="flex items-center gap-6 text-sm">
          <div class="flex flex-col items-center">
            <span class="font-bold text-indigo-600">{{ store.totalBooks }}</span>
            <span class="text-xs text-slate-400 uppercase tracking-wide">藏书</span>
          </div>
          <div class="flex flex-col items-center">
            <span class="font-bold text-indigo-600">{{ store.totalCategories }}</span>
            <span class="text-xs text-slate-400 uppercase tracking-wide">分类</span>
          </div>
        </div>
        <router-link
          v-else
          to="/"
          class="rounded-md px-3 py-1.5 text-sm text-slate-500 transition hover:bg-slate-100 hover:text-slate-800"
        >
          返回书架
        </router-link>
      </div>
    </header>
    <main class="flex-1">
      <router-view />
    </main>
  </div>
</template>
