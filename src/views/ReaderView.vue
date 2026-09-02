<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { FullScreen, ZoomIn, ZoomOut, ArrowLeft, ArrowRight, Notebook, ChatDotRound } from '@element-plus/icons-vue'
import AIChatPanel from '../components/AIChatPanel.vue'
import { useBooksStore } from '../stores/books'
import { useNotesStore } from '../stores/notes'
import PdfViewer from '../components/PdfViewer.vue'
import EpubViewer from '../components/EpubViewer.vue'
import MarkdownViewer from '../components/MarkdownViewer.vue'
import TextViewer from '../components/TextViewer.vue'
import DownloadCard from '../components/DownloadCard.vue'

const props = defineProps({
  id: { type: String, required: true },
})

const store = useBooksStore()
const notes = useNotesStore()
const book = computed(() => store.byId(props.id))

// 根据文件扩展名判断阅读器类型
const readerType = computed(() => {
  if (!book.value) return 'notfound'
  const ext = book.value.file.toLowerCase().split('.').pop()
  if (ext === 'pdf') return 'pdf'
  if (ext === 'epub') return 'epub'
  if (ext === 'md') return 'markdown'
  if (ext === 'txt') return 'text'
  return 'download' // mobi, rar 等其他格式
})

// AI 助手面板
const showAI = ref(false)

// 本地笔记面板
const showNotes = ref(false)
const noteDraft = ref('')
const bookNotes = computed(() => (book.value ? notes.byBook(book.value.id) : []))

function saveNote() {
  const text = noteDraft.value.trim()
  if (!text || !book.value) return
  notes.add(book.value.id, { text })
  noteDraft.value = ''
}

function formatNoteTime(ts) {
  return new Date(ts).toLocaleString('zh-CN', { hour12: false })
}

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

onMounted(() => {
  document.addEventListener('fullscreenchange', onFullscreenChange)
})

onBeforeUnmount(() => {
  document.removeEventListener('fullscreenchange', onFullscreenChange)
})
</script>

<template>
  <div v-if="book" ref="containerRef" class="flex h-screen flex-col">
    <!-- 统一标题栏（响应式自适应） -->
    <div class="shrink-0 flex flex-wrap items-center gap-x-2 gap-y-1 border-b border-slate-200 bg-white px-2 py-1.5 sm:px-3 sm:py-2">
      <!-- 左侧：翻页（仅 PDF） -->
      <template v-if="readerType === 'pdf'">
        <el-button-group>
          <el-button :icon="ArrowLeft" :disabled="pdfViewerRef?.pageNum <= 1" @click="pdfViewerRef?.prev()">
            <span class="hidden sm:inline">上一页</span>
          </el-button>
          <el-button :icon="ArrowRight" :disabled="pdfViewerRef?.pageNum >= pdfViewerRef?.pageCount" @click="pdfViewerRef?.next()">
            <span class="hidden sm:inline">下一页</span>
          </el-button>
        </el-button-group>
        <div class="flex items-center gap-1 text-sm text-slate-600">
          <el-input-number
            :model-value="pdfViewerRef?.pageNum"
            :min="1"
            :max="pdfViewerRef?.pageCount || 1"
            :controls="false"
            size="small"
            class="!w-16 sm:!w-20"
            @change="(v) => pdfViewerRef?.goPage(v)"
          />
          <span>/ {{ pdfViewerRef?.pageCount || 0 }}</span>
        </div>
      </template>

      <!-- 中间：标题 + 作者（手机端隐藏作者） -->
      <h2 class="min-w-0 flex-1 truncate text-sm font-semibold text-slate-800 px-1 sm:px-2">
        {{ book.title }}
        <span class="hidden sm:inline ml-2 font-normal text-slate-400">{{ book.author }}</span>
      </h2>

      <!-- 右侧：笔记 + 缩放 + 全屏 -->
      <div class="flex items-center gap-1 text-sm text-slate-600">
        <el-button :icon="ChatDotRound" circle size="small" :title="showAI ? '关闭 AI 助手' : 'AI 助手'" @click="showAI = !showAI" />
        <el-button :icon="Notebook" circle size="small" :title="showNotes ? '关闭笔记' : '笔记'" @click="showNotes = !showNotes" />
        <template v-if="readerType === 'pdf'">
          <el-button :icon="ZoomOut" circle size="small" @click="pdfZoomOut" />
          <span class="hidden sm:block w-14 select-none text-center text-xs text-slate-500">
            {{ pdfViewerRef ? Math.round(pdfViewerRef.scale * 100) : 120 }}%
          </span>
          <el-button :icon="ZoomIn" circle size="small" @click="pdfZoomIn" />
        </template>
        <el-button :icon="FullScreen" circle size="small" :title="isFullscreen ? '退出全屏' : '全屏'" @click="toggleFullscreen" />
      </div>
    </div>

    <!-- 内容区 + 笔记侧栏 -->
    <div class="flex min-h-0 flex-1">
      <div class="min-w-0 flex-1">
        <!-- PDF 阅读器 -->
        <PdfViewer v-if="readerType === 'pdf'" ref="pdfViewerRef" :book="book" />

        <!-- EPUB 阅读器 -->
        <EpubViewer v-else-if="readerType === 'epub'" :book="book" :file-url="fileUrl" />

        <!-- Markdown 阅读器 -->
        <MarkdownViewer v-else-if="readerType === 'markdown'" :book="book" :file-url="fileUrl" />

        <!-- TXT 阅读器 -->
        <TextViewer v-else-if="readerType === 'text'" :book="book" :file-url="fileUrl" />

        <!-- 下载卡片（mobi/rar 等） -->
        <DownloadCard v-else-if="readerType === 'download'" :book="book" :file-url="fileUrl" />
      </div>

      <!-- AI 助手面板 -->
      <aside v-if="showAI" class="flex w-72 shrink-0 flex-col border-l border-slate-200 bg-white sm:w-80">
        <AIChatPanel :book="book" />
      </aside>

      <!-- 笔记面板 -->
      <aside
        v-if="showNotes"
        class="flex w-72 shrink-0 flex-col border-l border-slate-200 bg-white sm:w-80"
      >
        <div class="border-b border-slate-200 p-3 text-sm font-semibold text-slate-700">
          我的笔记（{{ bookNotes.length }}）
        </div>
        <div class="flex shrink-0 flex-col gap-2 border-b border-slate-200 p-3">
          <el-input
            v-model="noteDraft"
            type="textarea"
            :rows="3"
            resize="none"
            placeholder="记录阅读想法、摘录、决策依据…"
          />
          <el-button type="primary" size="small" :disabled="!noteDraft.trim()" @click="saveNote">
            保存笔记
          </el-button>
        </div>
        <div class="min-h-0 flex-1 space-y-2 overflow-y-auto p-3">
          <div
            v-for="note in bookNotes"
            :key="note.id"
            class="group rounded-lg border border-slate-200 bg-slate-50 p-2.5"
          >
            <p class="whitespace-pre-wrap break-words text-sm text-slate-700">{{ note.text }}</p>
            <div class="mt-1.5 flex items-center justify-between text-xs text-slate-400">
              <span>{{ formatNoteTime(note.time) }}</span>
              <el-button size="small" text class="opacity-0 group-hover:opacity-100" @click="notes.remove(book.id, note.id)">
                删除
              </el-button>
            </div>
          </div>
          <p v-if="!bookNotes.length" class="py-6 text-center text-xs text-slate-400">还没有笔记</p>
        </div>
      </aside>
    </div>
  </div>

  <div v-else class="flex h-[70vh] flex-col items-center justify-center gap-4">
    <p class="text-slate-400">未找到该书籍</p>
    <router-link to="/">
      <el-button type="primary" round>返回书架</el-button>
    </router-link>
  </div>
</template>
