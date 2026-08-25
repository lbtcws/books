<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useProgressStore } from '../stores/progress'

const props = defineProps({
  book: { type: Object, required: true },
})

const router = useRouter()
const progress = useProgressStore()

const prog = computed(() => progress.getProgress(props.book.id))
const percent = computed(() => {
  if (!prog.value || !prog.value.total) return 0
  return Math.min(100, Math.round((prog.value.page / prog.value.total) * 100))
})

function open() {
  router.push({ name: 'reader', params: { id: props.book.id } })
}
</script>

<template>
  <div
    class="group flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-lg"
  >
    <div class="relative aspect-[4/5] overflow-hidden bg-slate-100">
      <el-image
        :src="book.cover"
        :alt="book.title"
        fit="cover"
        class="h-full w-full transition duration-300 group-hover:scale-105"
      >
        <template #error>
          <div
            class="flex h-full w-full items-center justify-center bg-gradient-to-br from-indigo-500 to-indigo-700 p-6 text-center text-sm font-medium text-white"
          >
            {{ book.title }}
          </div>
        </template>
      </el-image>
      <span
        class="absolute left-3 top-3 rounded-full bg-black/40 px-2.5 py-0.5 text-xs text-white backdrop-blur"
      >
        {{ book.category }}
      </span>
    </div>

    <div class="flex flex-1 flex-col p-4">
      <h3 class="line-clamp-2 font-semibold text-slate-800">{{ book.title }}</h3>
      <p class="mt-1 text-sm text-slate-500">{{ book.author }} · {{ book.year }}</p>
      <p class="mt-2 line-clamp-2 flex-1 text-sm text-slate-500">{{ book.description }}</p>

      <div v-if="percent > 0" class="mt-3">
        <div class="mb-1 flex items-center justify-between text-xs text-slate-400">
          <span>阅读进度</span>
          <span>{{ percent }}%</span>
        </div>
        <el-progress :percentage="percent" :stroke-width="6" :show-text="false" />
      </div>

      <el-button type="primary" class="mt-4 w-full" round @click="open">
        {{ percent > 0 ? '继续阅读' : '开始阅读' }}
      </el-button>
    </div>
  </div>
</template>
