<script setup>
import { computed, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import { ArrowLeft, ArrowRight, ZoomIn, ZoomOut, RefreshLeft } from '@element-plus/icons-vue'
import { useProgressStore } from '../stores/progress'
import * as pdfjsLib from 'pdfjs-dist'
import pdfjsWorkerUrl from 'pdfjs-dist/build/pdf.worker.min.js?url'

// 配置 worker（使用 npm 包自带的 worker 文件，保证版本一致）
pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorkerUrl

const props = defineProps({
  book: { type: Object, required: true },
})

const progress = useProgressStore()

const canvasRef = ref(null)
const scrollRef = ref(null)
const loading = ref(true)
const error = ref('')
const pageNum = ref(1)
const pageCount = ref(0)
const scale = ref(1.2)
// 使用 shallowRef 避免 Vue 深度代理破坏 PDF.js 对象的私有成员
const pdfDoc = shallowRef(null)

let renderTask = null
// 滚动翻页相关状态
let scrollLock = false

const fileUrl = computed(() => import.meta.env.BASE_URL + 'books/' + encodeURIComponent(props.book.category) + '/' + encodeURIComponent(props.book.file))
const cMapUrl = import.meta.env.BASE_URL + 'cmaps/'
const zoomPercent = computed(() => Math.round(scale.value * 100))

async function loadPdf() {
  if (pdfDoc.value) {
    pdfDoc.value.destroy()
    pdfDoc.value = null
  }
  loading.value = true
  error.value = ''
  pageCount.value = 0
  try {
    const res = await fetch(fileUrl.value)
    if (!res.ok) throw new Error(`PDF 文件获取失败 (HTTP ${res.status})`)
    const buf = await res.arrayBuffer()
    const loadingTask = pdfjsLib.getDocument({
      data: buf,
      cMapUrl,
      cMapPacked: true,
    })
    const doc = await loadingTask.promise
    pdfDoc.value = doc
    pageCount.value = doc.numPages
    const saved = progress.getProgress(props.book.id)
    const start = saved ? Math.min(Math.max(1, saved.page), doc.numPages) : 1
    loading.value = false
    await renderPage(start)
  } catch (e) {
    console.error('[PdfViewer] load failed', e)
    error.value = `${e?.message || 'PDF 加载失败，请确认文件存在且未损坏'}\n\n${e?.stack || ''}`
    loading.value = false
  }
}

async function renderPage(num) {
  if (!pdfDoc.value) return
  const page = await pdfDoc.value.getPage(num)
  const viewport = page.getViewport({ scale: scale.value })
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const dpr = window.devicePixelRatio || 1

  if (renderTask) {
    renderTask.cancel()
    renderTask = null
  }

  canvas.width = Math.floor(viewport.width * dpr)
  canvas.height = Math.floor(viewport.height * dpr)
  canvas.style.width = `${Math.floor(viewport.width)}px`
  canvas.style.height = `${Math.floor(viewport.height)}px`

  const task = page.render({
    canvasContext: ctx,
    viewport,
    transform: dpr !== 1 ? [dpr, 0, 0, dpr, 0, 0] : null,
  })
  renderTask = task
  try {
    await task.promise
  } catch (e) {
    if (e?.name === 'RenderingCancelledException') return
    throw e
  } finally {
    renderTask = null
  }
  pageNum.value = num
  progress.setProgress(props.book.id, { page: num, total: pageCount.value })
  resetScroll()
}

// 切换分页后滚动位置归零，从头开始展示
function resetScroll() {
  const el = scrollRef.value
  if (!el) return
  scrollLock = true
  el.scrollTop = 0
  // 短暂锁定，避免重置滚动时误触发滚动翻页
  setTimeout(() => {
    scrollLock = false
  }, 200)
}

// 滚动翻页：滚到底部继续下滚 → 下一页；滚到顶部继续上滚 → 上一页
function onWheel(e) {
  const el = scrollRef.value
  if (!el || scrollLock || loading.value) return
  const max = el.scrollHeight - el.clientHeight
  if (max <= 0) return
  const atBottom = el.scrollTop >= max - 4
  const atTop = el.scrollTop <= 4
  if (e.deltaY > 0 && atBottom && pageNum.value < pageCount.value) {
    e.preventDefault()
    renderPage(pageNum.value + 1)
  } else if (e.deltaY < 0 && atTop && pageNum.value > 1) {
    e.preventDefault()
    renderPage(pageNum.value - 1)
  }
}

function goPage(val) {
  const n = Number(val)
  if (!Number.isInteger(n)) return
  const target = Math.min(Math.max(1, n), pageCount.value)
  if (target !== pageNum.value) renderPage(target)
  else pageNum.value = target
}

function prev() {
  if (pageNum.value > 1) renderPage(pageNum.value - 1)
}
function next() {
  if (pageNum.value < pageCount.value) renderPage(pageNum.value + 1)
}
function zoomIn() {
  scale.value = Math.min(3, +(scale.value + 0.2).toFixed(2))
  renderPage(pageNum.value)
}
function zoomOut() {
  scale.value = Math.max(0.5, +(scale.value - 0.2).toFixed(2))
  renderPage(pageNum.value)
}
function resetZoom() {
  scale.value = 1.2
  renderPage(pageNum.value)
}

function onKeydown(e) {
  const t = e.target
  if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return
  if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
    e.preventDefault()
    prev()
  } else if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {
    e.preventDefault()
    next()
  }
}

watch(() => props.book.id, loadPdf)

onMounted(() => {
  loadPdf()
  window.addEventListener('keydown', onKeydown)
  // passive: false 以便 preventDefault 阻止浏览器默认滚动
  scrollRef.value?.addEventListener('wheel', onWheel, { passive: false })
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  scrollRef.value?.removeEventListener('wheel', onWheel)
  if (renderTask) {
    renderTask.cancel()
    renderTask = null
  }
  if (pdfDoc.value) {
    pdfDoc.value.destroy()
    pdfDoc.value = null
  }
})
</script>

<template>
  <div class="flex h-full flex-col bg-slate-100">
    <!-- 工具栏 -->
    <div class="flex shrink-0 flex-wrap items-center gap-2 border-b border-slate-200 bg-white px-3 py-2">
      <el-button-group>
        <el-button :icon="ArrowLeft" :disabled="pageNum <= 1" @click="prev">上一页</el-button>
        <el-button :icon="ArrowRight" :disabled="pageNum >= pageCount" @click="next">下一页</el-button>
      </el-button-group>

      <div class="flex items-center gap-1 text-sm text-slate-600">
        <el-input-number
          v-model="pageNum"
          :min="1"
          :max="pageCount || 1"
          :controls="false"
          size="small"
          class="!w-20"
          @change="goPage"
        />
        <span>/ {{ pageCount }}</span>
      </div>

      <div class="flex-1" />

      <div class="flex items-center gap-1 text-sm text-slate-600">
        <el-button :icon="ZoomOut" circle size="small" @click="zoomOut" />
        <button
          class="w-14 select-none text-center text-xs text-slate-500 hover:text-indigo-600"
          title="重置缩放"
          @click="resetZoom"
        >
          {{ zoomPercent }}%
        </button>
        <el-button :icon="ZoomIn" circle size="small" @click="zoomIn" />
        <el-button :icon="RefreshLeft" circle size="small" title="重置缩放" @click="resetZoom" />
      </div>
    </div>

    <!-- 内容区 -->
    <div ref="scrollRef" class="min-h-0 flex-1 overflow-auto">
      <div v-if="loading" class="flex h-full items-center justify-center">
        <div class="flex flex-col items-center gap-3 text-slate-400">
          <el-icon class="is-loading" :size="28"><RefreshLeft /></el-icon>
          <span class="text-sm">正在加载 {{ book.title }}…</span>
        </div>
      </div>

      <el-result
        v-else-if="error"
        icon="error"
        title="加载失败"
        :sub-title="error"
        class="h-full"
      >
        <template #extra>
          <el-button type="primary" round @click="loadPdf">重试</el-button>
          <router-link to="/">
            <el-button round>返回书架</el-button>
          </router-link>
        </template>
      </el-result>

      <div v-else class="flex justify-center px-4 py-4">
        <canvas ref="canvasRef" class="rounded-md shadow-md" />
      </div>
    </div>
  </div>
</template>
