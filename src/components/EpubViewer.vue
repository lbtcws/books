<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef } from 'vue'
import { RefreshLeft } from '@element-plus/icons-vue'
import ePub from 'epubjs'
import { useProgressStore } from '../stores/progress'
import { useBookmarksStore } from '../stores/bookmarks'
import { applyAppTheme, themes } from '../services/theme'

const props = defineProps({
  book: { type: Object, required: true },
  fileUrl: { type: String, required: true },
})

const progress = useProgressStore()
const bookmarks = useBookmarksStore()

const containerRef = ref(null)
const loading = ref(true)
const error = ref('')
const toc = ref([])
const currentCfi = ref('')
const currentChapter = ref('')
const currentChapterHref = ref('')
const showToc = ref(false)
let scrollContainer = null
let lastScrollTop = 0
let isTurningPage = false

// epub.js 内部对象不能被 Vue 深度代理，使用 shallowRef
const rendition = shallowRef(null)
const epubBook = shallowRef(null)

// 阅读设置（持久化）
const SETTINGS_KEY = 'books-reader-epub-settings'
const settings = ref({ fontSize: 100, theme: 'light' })
try {
  Object.assign(settings.value, JSON.parse(localStorage.getItem(SETTINGS_KEY)) || {})
} catch {
  /* 忽略损坏的设置 */
}

function saveSettings() {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings.value))
}

function applyTheme() {
  const r = rendition.value
  if (!r) return
  const currentTheme = themes[settings.value.theme] || themes.light
  for (const [name, theme] of Object.entries(themes)) {
    r.themes.register(name, {
      body: theme,
      html: {
        backgroundColor: theme.background,
        scrollbarColor: `${theme.scrollbar} ${theme.background}`,
      },
      '::-webkit-scrollbar': { width: '10px', height: '10px' },
      '::-webkit-scrollbar-track': { background: theme.background },
      '::-webkit-scrollbar-thumb': {
        border: `2px solid ${theme.background}`,
        borderRadius: '999px',
        background: theme.scrollbar,
      },
    })
  }
  r.themes.select(settings.value.theme)
  if (containerRef.value) {
    containerRef.value.style.scrollbarColor = `${currentTheme.scrollbar} ${currentTheme.background}`
  }
}

function setFontSize(delta) {
  settings.value.fontSize = Math.min(200, Math.max(70, settings.value.fontSize + delta))
  rendition.value?.themes.fontSize(`${settings.value.fontSize}%`)
  saveSettings()
}

function setTheme(name) {
  settings.value.theme = name
  applyAppTheme(name)
  applyTheme()
  saveSettings()
}

const themeBackground = computed(() => themes[settings.value.theme]?.background || themes.light.background)
const themeColor = computed(() => themes[settings.value.theme]?.color || themes.light.color)

function toggleToc() {
  showToc.value = !showToc.value
}

function locationLabel() {
  const cfi = currentCfi.value
  if (!cfi) return ''
  // 用 CFI 作为书签定位信息，便于跳转
  return cfi
}

function normalizeHref(href) {
  if (!href) return ''
  const withoutFragment = String(href).split('#')[0]
  try {
    return decodeURIComponent(new URL(withoutFragment, 'https://epub.local/').pathname)
      .replace(/^\/+/, '')
  } catch {
    return decodeURIComponent(withoutFragment).replace(/^\/+/, '')
  }
}

function findChapterForHref(href) {
  const normalizedHref = normalizeHref(href)
  if (!normalizedHref) return null

  return toc.value
    .filter((item) => {
      const itemHref = normalizeHref(item.href)
      return itemHref && (itemHref === normalizedHref || normalizedHref.startsWith(`${itemHref}/`))
    })
    .sort((a, b) => normalizeHref(b.href).length - normalizeHref(a.href).length)[0] || null
}

function updateCurrentLocation(location) {
  currentCfi.value = location?.start?.cfi || ''
  const href = location?.start?.href || ''
  const chapter = findChapterForHref(href)
  currentChapterHref.value = normalizeHref(chapter?.href || href)
  currentChapter.value = chapter?.label || ''
  if (currentCfi.value) {
    localStorage.setItem(`books-reader-epub-progress:${props.book.id}`, currentCfi.value)
  }
}

function addBookmark() {
  if (!currentCfi.value) return
  const label = tocLabelFor(currentCfi.value) || props.book.title
  bookmarks.add(props.book.id, { cfi: currentCfi.value, label })
}

function tocLabelFor(cfi) {
  if (cfi === currentCfi.value && currentChapter.value) return currentChapter.value
  const loc = epubBook.value?.locations && epubBook.value.locations.locationFromCfi(cfi)
  return typeof loc === 'object' && loc?.href ? findChapterForHref(loc.href)?.label || '' : ''
}

function isCurrentChapter(item) {
  return normalizeHref(item.href) === currentChapterHref.value
}

async function getCurrentContext() {
  await nextTick()
  const frames = [...(containerRef.value?.querySelectorAll('iframe') || [])]
  const currentFrame = frames.find((frame) => normalizeHref(frame.contentDocument?.location?.href) === currentChapterHref.value)
    || frames.find((frame) => frame.contentDocument?.body?.innerText?.trim())
  const text = currentFrame?.contentDocument?.body?.innerText?.trim() || ''
  return text.slice(0, 16000)
}

async function goToBookmark(bm) {
  await rendition.value?.display(bm.cfi)
  await scrollToCurrentPageTop()
  showToc.value = false
}

async function goToToc(href) {
  await rendition.value?.display(href)
  await scrollToCurrentPageTop()
  showToc.value = false
}

async function scrollToCurrentPageTop() {
  await new Promise((resolve) => requestAnimationFrame(resolve))
  rendition.value?.manager?.container?.scrollTo?.({ top: 0, left: 0, behavior: 'auto' })
  containerRef.value?.scrollTo?.({ top: 0, left: 0, behavior: 'auto' })
}

function onScroll() {
  if (!scrollContainer || isTurningPage) return
  const { scrollTop, scrollHeight, clientHeight } = scrollContainer
  const reachedTop = scrollTop <= 8 && lastScrollTop > scrollTop
  const reachedBottom = scrollTop + clientHeight >= scrollHeight - 8 && scrollTop > lastScrollTop
  lastScrollTop = scrollTop
  if (reachedTop) prev()
  if (reachedBottom) next()
}

function bindScroll() {
  // 优先使用 epubjs 的 manager container
  const managerContainer = rendition.value?.manager?.container
  if (managerContainer) {
    scrollContainer = managerContainer
    lastScrollTop = scrollContainer.scrollTop
    scrollContainer.addEventListener('scroll', onScroll, { passive: true })
    return
  }

  // 回退到 containerRef
  const container = containerRef.value
  if (!container) return

  scrollContainer = container
  lastScrollTop = scrollContainer.scrollTop
  scrollContainer.addEventListener('scroll', onScroll, { passive: true })
}

function unbindScroll() {
  scrollContainer?.removeEventListener('scroll', onScroll)
  scrollContainer = null
}

async function prev() {
  if (isTurningPage) return
  isTurningPage = true
  try {
    await rendition.value?.prev()
    await scrollToCurrentPageTop()
  } finally {
    lastScrollTop = 0
    isTurningPage = false
  }
}

async function next() {
  if (isTurningPage) return
  isTurningPage = true
  try {
    await rendition.value?.next()
    await scrollToCurrentPageTop()
  } finally {
    lastScrollTop = 0
    isTurningPage = false
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

function flattenToc(list, depth = 0) {
  return (list || []).flatMap((item) => [
    { label: item.label, href: item.href, depth },
    ...flattenToc(item.subitems, depth + 1),
  ])
}

async function loadEpub() {
  loading.value = true
  error.value = ''
  destroyBook()
  try {
    const b = ePub(props.fileUrl)
    epubBook.value = b
    const r = b.renderTo(containerRef.value, {
      width: '100%',
      height: '100%',
      flow: 'scrolled-doc',
      spread: 'none',
    })
    rendition.value = r
    await b.loaded.metadata
    applyTheme()
    r.themes.fontSize(`${settings.value.fontSize}%`)

    const nav = await b.loaded.navigation
    toc.value = flattenToc(nav.toc)

    r.on('relocated', (location) => {
      updateCurrentLocation(location)
    })

    const savedCfi = localStorage.getItem(`books-reader-epub-progress:${props.book.id}`)
    await r.display(savedCfi || undefined)
    updateCurrentLocation(r.currentLocation())
    applyTheme()
    // 延迟绑定滚动监听，确保 DOM 已渲染
    await nextTick()
    bindScroll()
    loading.value = false
  } catch (e) {
    console.error('[EpubViewer] load failed', e)
    error.value = e?.message || 'EPUB 加载失败，请确认文件存在且未损坏'
    loading.value = false
  }
}

function destroyBook() {
  unbindScroll()
  try {
    rendition.value?.destroy()
    epubBook.value?.destroy()
  } catch {
    /* 忽略销毁异常 */
  }
  rendition.value = null
  epubBook.value = null
}

const pageLabel = computed(() => currentChapter.value || '正文')

defineExpose({ prev, next, setTheme, toggleToc, themeBackground, pageLabel, currentCfi, locationLabel, getCurrentContext })

onMounted(() => {
  loadEpub()
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  destroyBook()
})

const bookBookmarks = computed(() => bookmarks.byBook(props.book.id))
</script>

<template>
  <div class="relative flex h-full flex-col" :style="{ backgroundColor: themeBackground, color: themeColor }">
    <!-- 阅读区 -->
    <div class="relative min-h-0 flex-1" :style="{ backgroundColor: themeBackground }">
      <div v-if="loading" class="flex h-full items-center justify-center text-slate-400">
        <el-icon class="is-loading mr-2" :size="22"><RefreshLeft /></el-icon>
        正在加载 {{ book.title }}…
      </div>
      <el-result v-else-if="error" icon="error" title="加载失败" :sub-title="error" class="h-full">
        <template #extra>
          <el-button type="primary" round @click="loadEpub">重试</el-button>
        </template>
      </el-result>
      <div ref="containerRef" class="h-full w-full overflow-y-auto" :style="{ visibility: error ? 'hidden' : 'visible' }" />

      <!-- 悬浮翻页控件（底部边缘轻巧提示） -->
      <div v-if="!loading && !error" class="pointer-events-none absolute bottom-3 left-0 right-0 flex justify-center gap-3 px-4">
        <div
          class="pointer-events-auto flex items-center gap-2 rounded-full border px-3 py-1.5 shadow-md backdrop-blur transition hover:shadow-lg"
          :style="{ backgroundColor: themeBackground, color: themeColor, borderColor: themeColor }"
        >
          <el-button size="small" text :style="{ color: themeColor }" @click="prev">
            上一节
          </el-button>
          <span class="px-1 text-xs" :style="{ color: themeColor }">{{ pageLabel }}</span>
          <el-button size="small" text :style="{ color: themeColor }" @click="next">
            下一节
          </el-button>
        </div>
      </div>

      <!-- 目录 / 书签抽屉 -->
      <div
        v-if="showToc"
        class="absolute right-0 top-0 z-10 flex h-full w-72 flex-col border-l border-slate-200 bg-white shadow-lg"
        :style="{ backgroundColor: themeBackground, color: themeColor }"
      >
        <div class="flex items-center justify-between border-b border-slate-200 px-4 py-2">
          <span class="font-semibold text-slate-700">目录</span>
          <el-button size="small" text @click="showToc = false">关闭</el-button>
        </div>
        <div class="flex-1 overflow-y-auto p-2">
          <div
            v-for="(item, i) in toc"
            :key="i"
            class="cursor-pointer truncate rounded px-2 py-1.5 text-sm text-slate-600 hover:bg-indigo-50 hover:text-indigo-600"
            :class="{ 'bg-indigo-100 font-medium text-indigo-700': isCurrentChapter(item) }"
            :style="{ paddingLeft: `${8 + item.depth * 14}px` }"
            @click="goToToc(item.href)"
          >
            {{ item.label || '（无标题）' }}
          </div>
        </div>
        <div class="border-t border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700">书签</div>
        <div class="max-h-40 overflow-y-auto p-2">
          <div v-if="!bookBookmarks.length" class="px-2 py-1 text-xs text-slate-400">暂无书签</div>
          <div
            v-for="bm in bookBookmarks"
            :key="bm.id"
            class="group flex cursor-pointer items-center gap-1 rounded px-2 py-1.5 text-sm text-slate-600 hover:bg-indigo-50"
            @click="goToBookmark(bm)"
          >
            <span class="flex-1 truncate">{{ bm.label || bm.cfi }}</span>
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
