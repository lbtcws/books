<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { FullScreen, ZoomIn, ZoomOut, RefreshLeft, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
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
const pdfViewerRef = ref(null)

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

function pdfZoomIn() {
  pdfViewerRef.value?.zoomIn()
}
function pdfZoomOut() {
  pdfViewerRef.value?.zoomOut()
}
function pdfResetZoom() {
  pdfViewerRef.value?.resetZoom()
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
    <!-- 统一标题栏（所有文档类型共用） -->
    <div class="shrink-0 flex items-center gap-2 border-b border-slate-200 bg-white px-3 py-2">
      <!-- 左侧：翻页（仅 PDF） -->
      <template v-if="readerType === 'pdf'">
        <el-button-group>
          <el-button :icon="ArrowLeft" :disabled="pdfViewerRef?.pageNum <= 1" @click="pdfViewerRef?.prev()">上一页</el-button>
          <el-button :icon="ArrowRight" :disabled="pdfViewerRef?.pageNum >= pdfViewerRef?.pageCount" @click="pdfViewerRef?.next()">下一页</el-button>
        </el-button-group>
        <div class="flex items-center gap-1 text-sm text-slate-600">
          <el-input-number
            :model-value="pdfViewerRef?.pageNum"
            :min="1"
            :max="pdfViewerRef?.pageCount || 1"
            :controls="false"
            size="small"
            class="!w-20"
            @change="(v) => pdfViewerRef?.goPage(v)"
          />
          <span>/ {{ pdfViewerRef?.pageCount || 0 }}</span>
        </div>
      </template>

      <!-- 中间：标题 + 作者 -->
      <h2 class="min-w-0 flex-1 truncate text-sm font-semibold text-slate-800 px-2">
        {{ book.title }}
        <span class="ml-2 font-normal text-slate-400">{{ book.author }}</span>
      </h2>

      <!-- 右侧：缩放 + 全屏 -->
      <div class="flex items-center gap-1 text-sm text-slate-600">
        <template v-if="readerType === 'pdf'">
          <el-button :icon="ZoomOut" circle size="small" @click="pdfZoomOut" />
          <button
            class="w-14 select-none text-center text-xs text-slate-500 hover:text-indigo-600"
            title="重置缩放"
            @click="pdfResetZoom"
          >
            {{ pdfViewerRef ? Math.round(pdfViewerRef.scale * 100) : 120 }}%
          </button>
          <el-button :icon="ZoomIn" circle size="small" @click="pdfZoomIn" />
          <el-button :icon="RefreshLeft" circle size="small" title="重置缩放" @click="pdfResetZoom" />
        </template>
        <el-button :icon="FullScreen" circle size="small" :title="isFullscreen ? '退出全屏' : '全屏'" @click="toggleFullscreen" />
      </div>
    </div>

    <!-- 内容区 -->
    <div class="min-h-0 flex-1">
      <!-- PDF 阅读器 -->
      <PdfViewer v-if="readerType === 'pdf'" ref="pdfViewerRef" :book="book" />

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
