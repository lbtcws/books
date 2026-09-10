<script setup>
import { computed, nextTick, ref } from 'vue'
import { Promotion } from '@element-plus/icons-vue'
import { marked } from 'marked'
import { aiProvider } from '../services/ai/AIProvider'

const props = defineProps({
  book: { type: Object, required: true },
  getReaderContext: { type: Function, default: null },
})

const messages = ref([])
const input = ref('')
const busy = ref(false)
const listRef = ref(null)

const modeLabel = computed(() => (aiProvider.enabled ? 'AI Mode' : 'Static Mode'))

const bookContext = computed(() => [
  `当前书籍：${props.book.title || '未命名'}`,
  `作者：${props.book.author || '未知'}`,
  `格式：${props.book.fileName || props.book.file || '未知'}`,
  `简介：${props.book.summary || '暂无简介'}`,
].join('\n'))

async function getAIContext() {
  const chapter = await props.getReaderContext?.()
  return chapter ? `${bookContext.value}\n当前章节原文：\n${chapter}` : bookContext.value
}

function renderMarkdown(text) {
  const html = marked.parse(text || '', { breaks: true, gfm: true })
  if (typeof document === 'undefined') return html

  const parsed = new DOMParser().parseFromString(html, 'text/html')
  parsed.querySelectorAll('script, style, iframe, object, embed, form').forEach((node) => node.remove())
  parsed.querySelectorAll('*').forEach((node) => {
    for (const attribute of [...node.attributes]) {
      if (attribute.name.toLowerCase().startsWith('on')) node.removeAttribute(attribute.name)
    }
    if (['href', 'src'].includes(node.tagName === 'A' ? 'href' : 'src')) {
      const value = node.getAttribute(node.tagName === 'A' ? 'href' : 'src') || ''
      if (/^\s*javascript:/i.test(value)) node.removeAttribute(node.tagName === 'A' ? 'href' : 'src')
    }
  })
  return parsed.body.innerHTML
}

async function send() {
  const q = input.value.trim()
  if (!q || busy.value) return
  input.value = ''
  messages.value.push({ role: 'user', text: q })
  busy.value = true
  try {
    const res = await aiProvider.chat(q, await getAIContext())
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
        <p v-if="m.role === 'user'" class="whitespace-pre-wrap break-words">{{ m.text }}</p>
        <div v-else class="markdown-content break-words" v-html="renderMarkdown(m.text)" />
      </div>
      <p v-if="!messages.length" class="py-8 text-center text-xs text-slate-400">
        针对当前章节提问
      </p>
      <p v-if="busy" class="text-center text-xs text-slate-400">思考中…</p>
    </div>

    <div class="shrink-0 space-y-2 border-t border-slate-200 p-3">
      <div class="flex items-end gap-2">
        <el-input
          v-model="input"
          size="small"
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 6 }"
          resize="none"
          placeholder="提问当前章节内容…"
          :disabled="busy"
          @keydown.enter.exact.prevent="send"
        />
        <el-button class="mb-0.5" size="small" type="primary" :icon="Promotion" :disabled="busy || !input.trim()" @click="send" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.markdown-content :deep(p) {
  margin: 0 0 0.65rem;
}

.markdown-content :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  margin: 0.75rem 0 0.4rem;
  font-weight: 700;
  line-height: 1.35;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 0.45rem 0;
  padding-left: 1.25rem;
}

.markdown-content :deep(li) {
  margin: 0.2rem 0;
}

.markdown-content :deep(blockquote) {
  margin: 0.6rem 0;
  border-left: 3px solid #a5b4fc;
  padding-left: 0.7rem;
  color: #64748b;
}

.markdown-content :deep(code) {
  border-radius: 0.25rem;
  background: rgba(148, 163, 184, 0.18);
  padding: 0.1rem 0.3rem;
  font-size: 0.88em;
}

.markdown-content :deep(pre) {
  overflow-x: auto;
  margin: 0.6rem 0;
  border-radius: 0.35rem;
  background: rgba(15, 23, 42, 0.9);
  padding: 0.65rem;
  color: #e2e8f0;
}

.markdown-content :deep(pre code) {
  background: transparent;
  padding: 0;
}

.markdown-content :deep(a) {
  color: #4f46e5;
  text-decoration: underline;
}

.markdown-content :deep(table) {
  display: block;
  max-width: 100%;
  overflow-x: auto;
  border-collapse: collapse;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid rgba(148, 163, 184, 0.35);
  padding: 0.25rem 0.45rem;
  text-align: left;
}
</style>
