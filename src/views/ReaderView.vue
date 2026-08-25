<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { FullScreen } from '@element-plus/icons-vue'
import { useBooksStore } from '../stores/books'
import PdfViewer from '../components/PdfViewer.vue'
import MarkdownViewer from '../components/MarkdownViewer.vue'
import TextViewer from '../components/TextViewer.vue'
import DownloadCard from '../components/DownloadCard.vue'

const props = defineProps({
  id: { type: String, required: true },
})

const store = useBooksStore()
const book = computed(() => store.byId(props.id))

// 根据文件扩展名判断阅读器类型
const readerType = computed(() => {
  if (!book.value) return 'notfound'
  const ext = book.value.file.toLowerCase().split('.').pop()
  if (ext === 'pdf') return 'pdf'
  if (ext === 'md') return 'markdown'
  if (ext === 'txt') return 'text'
  return 'download' // epub, mobi, rar 等其他格式
})

const fileUrl = computed(() => {
  if (!book.value) return ''
  return import.meta.env.BASE_URL + 'books/' + encodeURIComponent(book.value.category) + '/' + encodeURIComponent(book.value.file)
})

// 全屏功能
const isFullscreen = ref(false)
const containerRef = ref(null)

function toggleFullscreen() {
  if (!containerRef.value) return
  if (!document.fullscreenElement) {
    containerRef.value.requestFullscreen().catch(() => {})
  } else {
    document.exitFullscreen().catch(() => {})
  }
}

function onFullscreenChange() {
  isFullscreen.value = !!document.fullscreenElement
}

onMounted(() => {
  document.addEventListener('fullscreenchange', onFullscreenChange)
})

onBeforeUnmount(() => {
  document.removeEventListener('fullscreenchange', onFullscreenChange)
})
</script>

<template>
  <div v-if="book" ref="containerRef" class="flex h-[calc(100vh-3.5rem)] flex-col">
    <!-- 标题栏 -->
    <div class="shrink-0 border-b border-slate-200 bg-white px-4 py-2.5">
      <div class="flex items-center gap-3">
        <h2 class="min-w-0 flex-1 truncate text-sm font-semibold text-slate-800">
          {{ book.title }}
          <span class="ml-2 font-normal text-slate-400">{{ book.author }}</span>
        </h2>
        <el-button :icon="FullScreen" circle size="small" :title="isFullscreen ? '退出全屏' : '全屏'" @click="toggleFullscreen" />
      </div>
    </div>

    <!-- 内容区 -->
    <div class="min-h-0 flex-1">
      <!-- PDF 阅读器 -->
      <PdfViewer v-if="readerType === 'pdf'" :book="book" />

      <!-- Markdown 阅读器 -->
      <MarkdownViewer v-else-if="readerType === 'markdown'" :book="book" :file-url="fileUrl" />

      <!-- TXT 阅读器 -->
      <TextViewer v-else-if="readerType === 'text'" :book="book" :file-url="fileUrl" />

      <!-- 下载卡片（epub/mobi/rar 等） -->
      <DownloadCard v-else-if="readerType === 'download'" :book="book" :file-url="fileUrl" />
    </div>
  </div>

  <div v-else class="flex h-[70vh] flex-col items-center justify-center gap-4">
    <p class="text-slate-400">未找到该书籍</p>
    <router-link to="/">
      <el-button type="primary" round>返回书架</el-button>
    </router-link>
  </div>
</template>
