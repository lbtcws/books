<script setup>
import { ref, onMounted, computed } from 'vue'
import { marked } from 'marked'
import { Loading } from '@element-plus/icons-vue'

const props = defineProps({
  book: { type: Object, required: true },
  fileUrl: { type: String, required: true },
})

const content = ref('')
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const res = await fetch(props.fileUrl)
    if (!res.ok) throw new Error(`文件获取失败 (HTTP ${res.status})`)
    const text = await res.text()
    content.value = marked.parse(text)
    loading.value = false
  } catch (e) {
    console.error('[MarkdownViewer] load failed', e)
    error.value = e.message || 'Markdown 加载失败'
    loading.value = false
  }
})
</script>

<template>
  <div class="h-full overflow-auto bg-slate-50">
    <div v-if="loading" class="flex h-full items-center justify-center">
      <div class="flex flex-col items-center gap-3 text-slate-400">
        <el-icon class="is-loading" :size="28"><Loading /></el-icon>
        <span class="text-sm">正在加载 {{ book.title }}...</span>
      </div>
    </div>

    <div v-else-if="error" class="flex h-full items-center justify-center">
      <el-result icon="error" title="加载失败" :sub-title="error" class="h-full">
        <template #extra>
          <router-link to="/">
            <el-button round>返回书架</el-button>
          </router-link>
        </template>
      </el-result>
    </div>

    <div v-else class="mx-auto max-w-4xl px-8 py-8">
      <div class="prose prose-slate max-w-none" v-html="content"></div>
    </div>
  </div>
</template>

<style scoped>
.prose {
  line-height: 1.8;
  color: #334155;
}

.prose :deep(h1),
.prose :deep(h2),
.prose :deep(h3),
.prose :deep(h4) {
  color: #1e293b;
  font-weight: 600;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}

.prose :deep(h1) {
  font-size: 2em;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.3em;
}

.prose :deep(h2) {
  font-size: 1.5em;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.3em;
}

.prose :deep(p) {
  margin: 1em 0;
}

.prose :deep(a) {
  color: #6366f1;
  text-decoration: none;
}

.prose :deep(a:hover) {
  text-decoration: underline;
}

.prose :deep(code) {
  background: #f1f5f9;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
  color: #e11d48;
}

.prose :deep(pre) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 1em;
  border-radius: 6px;
  overflow-x: auto;
}

.prose :deep(pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
}

.prose :deep(blockquote) {
  border-left: 4px solid #6366f1;
  padding-left: 1em;
  margin: 1em 0;
  color: #64748b;
}

.prose :deep(ul),
.prose :deep(ol) {
  margin: 1em 0;
  padding-left: 2em;
}

.prose :deep(li) {
  margin: 0.5em 0;
}

.prose :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
}

.prose :deep(th),
.prose :deep(td) {
  border: 1px solid #e2e8f0;
  padding: 0.5em 1em;
  text-align: left;
}

.prose :deep(th) {
  background: #f8fafc;
  font-weight: 600;
}
</style>
