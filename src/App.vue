<script setup>
import { useRoute } from 'vue-router'
import { useRouter } from 'vue-router'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { HomeFilled } from '@element-plus/icons-vue'
import { useBooksStore } from './stores/books'

const route = useRoute()
const router = useRouter()
const store = useBooksStore()
const isReader = computed(() => route.name === 'reader')
const HOME_BUTTON_KEY = 'books-home-button-position'
const homeButton = ref({ left: 24, top: 0 })
const isDragging = ref(false)
const hasDragged = ref(false)
const suppressHomeClickUntil = ref(0)
let dragOffset = { x: 0, y: 0 }

function clampHomeButton(left, top) {
  const width = 48
  const margin = 16
  return {
    left: Math.max(margin, Math.min(left, window.innerWidth - width - margin)),
    top: Math.max(margin, Math.min(top, window.innerHeight - width - margin)),
  }
}

function saveHomeButtonPosition() {
  localStorage.setItem(HOME_BUTTON_KEY, JSON.stringify(homeButton.value))
}

function onHomeButtonPointerDown(event) {
  if (event.button !== 0) return
  event.preventDefault()
  event.currentTarget.setPointerCapture?.(event.pointerId)
  const rect = event.currentTarget.getBoundingClientRect()
  dragOffset = { x: event.clientX - rect.left, y: event.clientY - rect.top }
  isDragging.value = true
  hasDragged.value = false
}

function onHomeButtonPointerMove(event) {
  if (!isDragging.value) return
  event.preventDefault()
  const next = clampHomeButton(event.clientX - dragOffset.x, event.clientY - dragOffset.y)
  if (Math.abs(next.left - homeButton.value.left) > 2 || Math.abs(next.top - homeButton.value.top) > 2) {
    hasDragged.value = true
    event.preventDefault()
  }
  homeButton.value = next
}

function onHomeButtonPointerUp(event) {
  if (!isDragging.value) return
  isDragging.value = false
  if (hasDragged.value) suppressHomeClickUntil.value = Date.now() + 300
  event?.currentTarget?.releasePointerCapture?.(event.pointerId)
  saveHomeButtonPosition()
}

function onHomeButtonPointerCancel() {
  if (!isDragging.value) return
  isDragging.value = false
  saveHomeButtonPosition()
}

function onHomeButtonClick(event) {
  if (hasDragged.value || Date.now() < suppressHomeClickUntil.value) {
    event.preventDefault()
    event.stopPropagation()
    hasDragged.value = false
    return
  }
  router.push('/')
}

function onWindowResize() {
  homeButton.value = clampHomeButton(homeButton.value.left, homeButton.value.top)
}

onMounted(() => {
  try {
    const saved = JSON.parse(localStorage.getItem(HOME_BUTTON_KEY) || 'null')
    if (saved?.left != null && saved?.top != null) {
      homeButton.value = clampHomeButton(saved.left, saved.top)
    } else {
      homeButton.value = clampHomeButton(24, window.innerHeight - 64)
    }
  } catch {
    homeButton.value = clampHomeButton(24, window.innerHeight - 64)
  }
  window.addEventListener('resize', onWindowResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onWindowResize)
})
</script>

<template>
  <div class="flex min-h-full flex-col">
    <main class="flex-1">
      <router-view />
    </main>

    <!-- 右下角悬浮首页按钮（阅读页显示） -->
    <button
      v-if="isReader"
      type="button"
      class="fixed z-50 flex h-12 w-12 items-center justify-center rounded-full border shadow-lg transition-shadow hover:shadow-xl"
      :class="isDragging ? 'cursor-grabbing scale-105' : 'cursor-grab'"
      :style="{ left: `${homeButton.left}px`, top: `${homeButton.top}px`, backgroundColor: 'var(--app-background)', color: 'var(--app-foreground)', borderColor: 'var(--app-foreground)', touchAction: 'none', userSelect: 'none' }"
      title="返回书架"
      @pointerdown="onHomeButtonPointerDown"
      @pointermove="onHomeButtonPointerMove"
      @pointerup="onHomeButtonPointerUp"
      @pointercancel="onHomeButtonPointerCancel"
      @click="onHomeButtonClick"
    >
      <el-icon :size="22"><HomeFilled /></el-icon>
    </button>
  </div>
</template>
