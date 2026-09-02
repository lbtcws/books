<script setup>
import { computed, nextTick, ref } from 'vue'
import { Promotion } from '@element-plus/icons-vue'
import { aiProvider } from '../services/ai/AIProvider'

const props = defineProps({
  book: { type: Object, required: true },
})

const messages = ref([])
const input = ref('')
const busy = ref(false)
const listRef = ref(null)

const modeLabel = computed(() => (aiProvider.enabled ? 'AI Mode' : 'Static Mode'))

async function send() {
  const q = input.value.trim()
  if (!q || busy.value) return
  input.value = ''
  messages.value.push({ role: 'user', text: q })
  busy.value = true
  try {
    const res = await aiProvider.chat(q)
    messages.value.push({
      role: 'ai',
      text: res.answer || res.error || '（无回答）',
      sources: res.sources || [],
      disabled: !res.enabled,
    })
  } finally {
    busy.value = false
    nextTick(() => {
      if (listRef.value) listRef.value.scrollTop = listRef.value.scrollHeight
    })
  }
}

async function summarize() {
  if (busy.value) return
  busy.value = true
  messages.value.push({ role: 'user', text: `请总结《${props.book.title}》的核心内容` })
  try {
    const res = await aiProvider.summary(props.book.summary || props.book.title)
    messages.value.push({
      role: 'ai',
      text: res.answer || res.error || '（无回答）',
      disabled: !res.enabled,
    })
  } finally {
    busy.value = false
    nextTick(() => {
      if (listRef.value) listRef.value.scrollTop = listRef.value.scrollHeight
    })
  }
}
</script>

<template>
  <div class="flex h-full flex-col">
    <div class="flex shrink-0 items-center justify-between border-b border-slate-200 px-3 py-2">
      <span class="text-sm font-semibold text-slate-700">AI 助手</span>
      <el-tag size="small" :type="aiProvider.enabled ? 'success' : 'info'">{{ modeLabel }}</el-tag>
    </div>

    <div ref="listRef" class="min-h-0 flex-1 space-y-3 overflow-y-auto p-3">
      <div
        v-for="(m, i) in messages"
        :key="i"
        class="rounded-lg px-3 py-2 text-sm"
        :class="m.role === 'user' ? 'ml-8 bg-indigo-50 text-indigo-700' : 'mr-8 bg-slate-100 text-slate-700'"
      >
        <p class="whitespace-pre-wrap break-words">{{ m.text }}</p>
        <div v-if="m.sources?.length" class="mt-2 border-t border-slate-200 pt-1.5 text-xs text-slate-400">
          出处：<span v-for="(s, j) in m.sources" :key="j" class="mr-2">📚 {{ s.title }}</span>
        </div>
      </div>
      <p v-if="!messages.length" class="py-8 text-center text-xs text-slate-400">
        向你的知识库提问，或点击"总结本书"
      </p>
      <p v-if="busy" class="text-center text-xs text-slate-400">思考中…</p>
    </div>

    <div class="shrink-0 space-y-2 border-t border-slate-200 p-3">
      <el-button size="small" plain class="w-full" :disabled="busy" @click="summarize">
        总结本书
      </el-button>
      <div class="flex gap-2">
        <el-input
          v-model="input"
          size="small"
          placeholder="提问，如：这本书讲了什么？"
          :disabled="busy"
          @keyup.enter="send"
        />
        <el-button size="small" type="primary" :icon="Promotion" :disabled="busy || !input.trim()" @click="send" />
      </div>
    </div>
  </div>
</template>
