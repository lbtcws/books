<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef } from 'vue'
import { RefreshLeft } from '@element-plus/icons-vue'
import { loadMobiBook } from '../services/mobi'
import { useProgressStore } from '../stores/progress'
import { useBookmarksStore } from '../stores/bookmarks'
import { applyAppTheme, loadSavedTheme, themes } from '../services/theme'

const props = defineProps({
  book: { type: Object, required: true },
  fileUrl: { type: String, required: true },
})

const progress = useProgressStore()
const bookmarks = useBookmarksStore()

const iframeRef = ref(null)
const loading = ref(true)
const error = ref('')
const toc = ref([])
const showToc = ref(false)

const mobiInstance = shallowRef(null)
const bookInstance = shallowRef(null)

const sections = ref([])
const currentSectionIndex = ref(0)
const sectionCount = computed(() => sections.value.length || 1)
const pendingAnchorSelector = ref(null)

// 阅读设置持久化
const SETTINGS_KEY = 'books-reader-mobi-settings'
const settings = ref({
  fontSize: 100,
  theme: loadSavedTheme(),
})

try {
  const saved = JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}')
  if (saved.fontSize) settings.value.fontSize = saved.fontSize
  if (saved.theme) settings.value.theme = saved.theme
} catch {
  /* 忽略损坏的设置 */
}

function saveSettings() {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings.value))
}

const themeBackground = computed(() => themes[settings.value.theme]?.background || themes.light.background)
const themeColor = computed(() => themes[settings.value.theme]?.color || themes.light.color)

function setTheme(name) {
  settings.value.theme = name
  applyAppTheme(name)
  applyIframeTheme()
  saveSettings()
}

function setFontSize(delta) {
  settings.value.fontSize = Math.min(200, Math.max(70, settings.value.fontSize + delta))
  applyIframeTheme()
  saveSettings()
}

function toggleToc() {
  showToc.value = !showToc.value
}

// 提取与打平目录
function flattenToc(list, depth = 0) {
  if (!list || !Array.isArray(list)) return []
  return list.flatMap((item) => [
    { label: item.label || '正文', href: item.href, depth },
    ...flattenToc(item.subitems, depth + 1),
  ])
}

// 建立默认备用目录
function buildFallbackToc(book) {
  if (!book?.sections || book.sections.length === 0) return []
  return book.sections.map((_, i) => ({
    label: `第 ${i + 1} 节`,
    href: `section:${i}`,
    depth: 0,
    sectionIndex: i,
  }))
}

const currentChapterLabel = computed(() => {
  const item = toc.value.find((t) => {
    if (t.sectionIndex === currentSectionIndex.value) return true
    if (t.href?.startsWith('filepos:') && bookInstance.value?.resolveHref) {
      try {
        const { index } = bookInstance.value.resolveHref(t.href)
        return index === currentSectionIndex.value
      } catch {
        return false
      }
    }
    return false
  })
  return item?.label || `第 ${currentSectionIndex.value + 1} 节`
})

const pageLabel = computed(() => currentChapterLabel.value)
const sectionLabel = computed(() => currentChapterLabel.value)

// 注入样式到 iframe
function applyIframeTheme() {
  const doc = iframeRef.value?.contentDocument
  if (!doc) return
  let styleEl = doc.getElementById('mobi-viewer-style')
  if (!styleEl) {
    styleEl = doc.createElement('style')
    styleEl.id = 'mobi-viewer-style'
    doc.head?.appendChild(styleEl)
  }
  const bg = themeBackground.value
  const fg = themeColor.value
  const size = settings.value.fontSize

  styleEl.textContent = `
    html {
      background-color: ${bg} !important;
      color: ${fg} !important;
      scrollbar-color: ${themes[settings.value.theme]?.scrollbar || '#c4c8c2'} ${bg} !important;
      margin: 0 !important;
      padding: 0 !important;
      box-sizing: border-box;
      font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', -apple-system, system-ui, sans-serif !important;
      -webkit-font-smoothing: antialiased;
      overflow-x: hidden !important;
    }
    body {
      max-width: 820px !important;
      margin: 0 auto !important;
      padding: 32px 24px 80px 24px !important;
      font-size: ${size}% !important;
      line-height: 1.85 !important;
      word-break: break-word !important;
      overflow-wrap: break-word !important;
    }
    ::-webkit-scrollbar {
      width: 10px !important;
      height: 10px !important;
    }
    ::-webkit-scrollbar-track {
      background: ${bg} !important;
    }
    ::-webkit-scrollbar-thumb {
      border: 2px solid ${bg} !important;
      border-radius: 999px !important;
      background: ${themes[settings.value.theme]?.scrollbar || '#c4c8c2'} !important;
    }
    img, image, svg {
      max-width: 100% !important;
      height: auto !important;
      display: block !important;
      margin: 16px auto !important;
      border-radius: 4px;
    }
    a {
      color: #6366f1 !important;
      text-decoration: underline;
      cursor: pointer;
    }
    a:hover {
      color: #4f46e5 !important;
    }
    p {
      margin-block-start: 0.8em !important;
      margin-block-end: 0.8em !important;
      text-indent: 2em;
    }
    blockquote {
      margin: 1em 0 !important;
      padding: 0.5em 1em !important;
      border-left: 4px solid #818cf8 !important;
      background-color: rgba(129, 140, 248, 0.08) !important;
      border-radius: 2px;
    }
    h1, h2, h3, h4, h5, h6 {
      color: ${fg} !important;
      font-weight: 600 !important;
      margin-top: 1.4em !important;
      margin-bottom: 0.6em !important;
      line-height: 1.35 !important;
    }
    table {
      border-collapse: collapse;
      width: 100%;
      margin: 1em 0;
    }
    th, td {
      border: 1px solid rgba(128, 128, 128, 0.3);
      padding: 6px 10px;
    }
  `
}

// 绑定 iframe 内部交互
function setupIframeListeners() {
  const win = iframeRef.value?.contentWindow
  const doc = iframeRef.value?.contentDocument
  if (!win || !doc) return

  // 键盘快捷键监听
  doc.addEventListener('keydown', onKeydown)

  // 内部链接捕获
  doc.addEventListener('click', (e) => {
    const a = e.target.closest('a')
    if (!a) return
    const filepos = a.getAttribute('filepos')
    const href = a.getAttribute('href') || ''

    if (filepos) {
      e.preventDefault()
      goToHref(`filepos:${filepos}`)
    } else if (href.startsWith('filepos:') || href.startsWith('kindle:pos:')) {
      e.preventDefault()
      goToHref(href)
    } else if (href.startsWith('#')) {
      e.preventDefault()
      const targetId = href.slice(1)
      const targetEl = doc.getElementById(targetId) || doc.querySelector(`[name="${targetId}"]`)
      targetEl?.scrollIntoView({ behavior: 'smooth' })
    } else if (href && !href.startsWith('javascript:')) {
      a.setAttribute('target', '_blank')
    }
  })

  // 滚动监听 - 在 window 和 document 上都监听（兼容不同浏览器）
  win.addEventListener('scroll', onScroll, { passive: true })
  doc.addEventListener('scroll', onScroll, { passive: true })
}

let isTurningSection = false
let scrollDebounceTimer = null
let lastScrollTop = 0

function getScrollMetrics() {
  const win = iframeRef.value?.contentWindow
  const doc = iframeRef.value?.contentDocument
  if (!win || !doc) return null
  // 滚动可能发生在 documentElement 或 body 上，取最大值
  const docScrollTop = doc.documentElement?.scrollTop || 0
  const bodyScrollTop = doc.body?.scrollTop || 0
  const scrollTop = Math.max(win.scrollY || 0, docScrollTop, bodyScrollTop)
  const scrollHeight = Math.max(doc.documentElement?.scrollHeight || 0, doc.body?.scrollHeight || 0) || 1
  const clientHeight = win.innerHeight || doc.documentElement?.clientHeight || 1
  return { scrollTop, scrollHeight, clientHeight }
}

function onScroll() {
  const metrics = getScrollMetrics()
  if (!metrics) return
  const { scrollTop, scrollHeight, clientHeight } = metrics
  const ratio = Math.min(1, Math.max(0, scrollTop / (scrollHeight - clientHeight || 1)))

  // 边界滚动监测：需要方向判断
  if (!isTurningSection) {
    // 向上滚动到顶部 -> 上一节
    const atTop = scrollTop <= 5 && lastScrollTop > scrollTop && currentSectionIndex.value > 0
    // 向下滚动到底部 -> 下一节
    const atBottom = scrollTop + clientHeight >= scrollHeight - 5 && scrollTop > lastScrollTop && currentSectionIndex.value < sectionCount.value - 1

    if (atTop || atBottom) {
      clearTimeout(scrollDebounceTimer)
      scrollDebounceTimer = setTimeout(() => {
        if (isTurningSection) return
        const current = getScrollMetrics()
        if (!current) return
        // 再次确认仍在边界
        const nowAtTop = current.scrollTop <= 5 && currentSectionIndex.value > 0
        const nowAtBottom = current.scrollTop + current.clientHeight >= current.scrollHeight - 5 && currentSectionIndex.value < sectionCount.value - 1
        if (nowAtTop) {
          isTurningSection = true
          prev({ scrollToBottom: true })
        } else if (nowAtBottom) {
          isTurningSection = true
          next()
        }
      }, 200)
    }
  }
  lastScrollTop = scrollTop

  // 保存阅读位置到 localStorage
  try {
    const progressData = {
      sectionIndex: currentSectionIndex.value,
      ratio,
    }
    localStorage.setItem(`books-reader-mobi-progress:${props.book.id}`, JSON.stringify(progressData))
  } catch {}

  // 同步进度到 Pinia Store
  const total = sectionCount.value
  const page = currentSectionIndex.value + 1
  progress.setProgress(props.book.id, { page, total })
}

// 加载指定分节
async function loadSection(index, anchorSelector = null) {
  if (!sections.value.length) return
  const validIndex = Math.max(0, Math.min(sections.value.length - 1, index))
  currentSectionIndex.value = validIndex
  pendingAnchorSelector.value = anchorSelector

  const section = sections.value[validIndex]
  if (!section) return

  try {
    const url = await section.load()
    if (iframeRef.value) {
      iframeRef.value.src = url
    }
  } catch (err) {
    console.error('[MobiViewer] Failed to load section:', validIndex, err)
    isTurningSection = false
  }
}

// iframe 渲染完成回调
async function onIframeLoaded() {
  applyIframeTheme()
  setupIframeListeners()

  // 重置滚动状态，允许新的滚动切节触发
  isTurningSection = false

  await nextTick()
  const doc = iframeRef.value?.contentDocument
  if (!doc) return

  // 滚动到指定锚点
  if (pendingAnchorSelector.value) {
    let el = null
    if (typeof pendingAnchorSelector.value === 'function') {
      el = pendingAnchorSelector.value(doc)
    } else if (typeof pendingAnchorSelector.value === 'string') {
      el = doc.querySelector(pendingAnchorSelector.value) || doc.getElementById(pendingAnchorSelector.value)
    }
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' })
    }
    pendingAnchorSelector.value = null
  } else {
    // 检查是否有恢复的滚动位置
    try {
      const saved = JSON.parse(localStorage.getItem(`books-reader-mobi-progress:${props.book.id}`) || '{}')
      if (saved.sectionIndex === currentSectionIndex.value && saved.ratio) {
        const win = iframeRef.value?.contentWindow
        const scrollHeight = doc.documentElement.scrollHeight || 1
        const clientHeight = win?.innerHeight || doc.documentElement.clientHeight || 1
        const targetScroll = saved.ratio * (scrollHeight - clientHeight)
        win?.scrollTo({ top: targetScroll, behavior: 'auto' })
        lastScrollTop = targetScroll
      }
    } catch {}
  }
}

// 跳转到指定目录或链接
async function goToHref(href) {
  if (!href || !bookInstance.value) return
  showToc.value = false

  if (href.startsWith('section:')) {
    const idx = parseInt(href.split(':')[1], 10)
    await loadSection(idx)
    return
  }

  if (href.startsWith('filepos:') || href.startsWith('kindle:pos:')) {
    try {
      const { index, anchor } = bookInstance.value.resolveHref(href)
      if (index !== currentSectionIndex.value) {
        await loadSection(index, anchor)
      } else {
        const doc = iframeRef.value?.contentDocument
        const el = anchor?.(doc)
        el?.scrollIntoView({ behavior: 'smooth' })
      }
    } catch (e) {
      console.warn('[MobiViewer] Failed to resolve href:', href, e)
    }
  }
}

async function prev() {
  if (currentSectionIndex.value > 0) {
    await loadSection(currentSectionIndex.value - 1)
  }
}

async function next() {
  if (currentSectionIndex.value < sectionCount.value - 1) {
    await loadSection(currentSectionIndex.value + 1)
  }
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

// 书签
const bookBookmarks = computed(() => bookmarks.byBook(props.book.id))

function addBookmark() {
  const label = `${currentChapterLabel.value} (第 ${currentSectionIndex.value + 1} 节)`
  bookmarks.add(props.book.id, {
    sectionIndex: currentSectionIndex.value,
    label,
  })
}

async function goToBookmark(bm) {
  if (bm.sectionIndex != null) {
    await loadSection(bm.sectionIndex)
  } else if (bm.href) {
    await goToHref(bm.href)
  }
  showToc.value = false
}

async function getCurrentContext() {
  await nextTick()
  return iframeRef.value?.contentDocument?.body?.innerText?.trim()?.slice(0, 16000) || ''
}

// 初始化加载 MOBI 文件
async function loadMobi() {
  loading.value = true
  error.value = ''
  destroyBook()

  try {
    const res = await fetch(props.fileUrl)
    if (!res.ok) throw new Error(`文件获取失败 (HTTP ${res.status})`)
    const arrayBuffer = await res.arrayBuffer()

    const { mobi, book } = await loadMobiBook(arrayBuffer)
    mobiInstance.value = mobi
    bookInstance.value = book

    sections.value = book.sections || []

    // 目录解析与回退
    if (book.toc && book.toc.length > 0) {
      toc.value = flattenToc(book.toc)
    } else {
      toc.value = buildFallbackToc(book)
    }

    // 恢复历史阅读进度
    let startSection = 0
    try {
      const saved = JSON.parse(localStorage.getItem(`books-reader-mobi-progress:${props.book.id}`) || '{}')
      if (typeof saved.sectionIndex === 'number' && saved.sectionIndex < sections.value.length) {
        startSection = saved.sectionIndex
      }
    } catch {}

    loading.value = false
    await nextTick()
    await loadSection(startSection)
  } catch (err) {
    console.error('[MobiViewer] load failed', err)
    error.value = err.message || 'MOBI 文件加载解析失败，请确认文件未损坏'
    loading.value = false
  }
}

function destroyBook() {
  try {
    bookInstance.value?.destroy?.()
  } catch {}
  bookInstance.value = null
  mobiInstance.value = null
  sections.value = []
}

defineExpose({
  prev,
  next,
  setTheme,
  setFontSize,
  toggleToc,
  addBookmark,
  themeBackground,
  pageLabel,
  sectionLabel,
  currentSectionIndex,
  sectionCount,
  getCurrentContext,
})

onMounted(() => {
  loadMobi()
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  destroyBook()
})
</script>

<template>
  <div class="relative flex h-full flex-col" :style="{ backgroundColor: themeBackground, color: themeColor }">
    <!-- 核心阅读区 -->
    <div class="relative min-h-0 flex-1" :style="{ backgroundColor: themeBackground }">
      <div v-if="loading" class="flex h-full items-center justify-center text-slate-400">
        <el-icon class="is-loading mr-2" :size="22"><RefreshLeft /></el-icon>
        正在加载 {{ book.title }}…
      </div>

      <el-result v-else-if="error" icon="error" title="加载失败" :sub-title="error" class="h-full">
        <template #extra>
          <el-button type="primary" round @click="loadMobi">重试</el-button>
        </template>
      </el-result>

      <div v-show="!loading && !error" class="relative h-full w-full">
        <iframe
          ref="iframeRef"
          class="h-full w-full border-0"
          :title="book.title"
          @load="onIframeLoaded"
        />

        <!-- 悬浮翻页控件（底部边缘轻巧提示） -->
        <div class="pointer-events-none absolute bottom-3 left-0 right-0 flex justify-center gap-3 px-4">
          <div
            class="pointer-events-auto flex items-center gap-2 rounded-full border px-3 py-1.5 shadow-md backdrop-blur transition hover:shadow-lg"
            :style="{ backgroundColor: themeBackground, color: themeColor, borderColor: themeColor }"
          >
            <el-button
              size="small"
              text
              :disabled="currentSectionIndex <= 0"
              :style="{ color: themeColor }"
              @click="prev"
            >
              上一节
            </el-button>
            <span class="px-1 text-xs" :style="{ color: themeColor }">
              {{ currentSectionIndex + 1 }} / {{ sectionCount }}
            </span>
            <el-button
              size="small"
              text
              :disabled="currentSectionIndex >= sectionCount - 1"
              :style="{ color: themeColor }"
              @click="next"
            >
              下一节
            </el-button>
          </div>
        </div>
      </div>

      <!-- 目录 / 书签抽屉 -->
      <div
        v-if="showToc"
        class="absolute right-0 top-0 z-10 flex h-full w-80 flex-col border-l border-slate-200 bg-white shadow-xl transition-all"
        :style="{ backgroundColor: themeBackground, color: themeColor }"
      >
        <div class="flex items-center justify-between border-b border-slate-200 px-4 py-2.5">
          <span class="font-semibold text-slate-700">目录与书签</span>
          <div class="flex items-center gap-2">
            <el-button size="small" text type="primary" @click="addBookmark">添加书签</el-button>
            <el-button size="small" text @click="showToc = false">关闭</el-button>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-2">
          <div class="mb-2 px-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">书籍目录</div>
          <div
            v-for="(item, i) in toc"
            :key="i"
            class="cursor-pointer truncate rounded px-2.5 py-1.5 text-sm text-slate-600 transition hover:bg-indigo-50 hover:text-indigo-600"
            :class="{ '!bg-indigo-100 !text-indigo-700 font-medium': currentChapterLabel === item.label }"
            :style="{ paddingLeft: `${10 + item.depth * 14}px` }"
            @click="goToHref(item.href)"
          >
            {{ item.label || '（无标题）' }}
          </div>
        </div>

        <div class="border-t border-slate-200 px-4 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          我的书签（{{ bookBookmarks.length }}）
        </div>
        <div class="max-h-48 overflow-y-auto p-2">
          <div v-if="!bookBookmarks.length" class="px-2 py-3 text-center text-xs text-slate-400">
            当前书籍暂无书签
          </div>
          <div
            v-for="bm in bookBookmarks"
            :key="bm.id"
            class="group flex cursor-pointer items-center gap-1.5 rounded px-2.5 py-1.5 text-sm text-slate-600 transition hover:bg-indigo-50"
            @click="goToBookmark(bm)"
          >
            <span class="flex-1 truncate text-xs">{{ bm.label }}</span>
            <el-button
              size="small"
              text
              class="opacity-0 group-hover:opacity-100"
              @click.stop="bookmarks.remove(book.id, bm.id)"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
iframe {
  display: block;
}
</style>

