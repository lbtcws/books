<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import { HomeFilled } from '@element-plus/icons-vue'
import { useBooksStore } from './stores/books'

const route = useRoute()
const store = useBooksStore()
const isReader = computed(() => route.name === 'reader')
</script>

<template>
  <div class="flex min-h-full flex-col">
    <main class="flex-1">
      <router-view />
    </main>

    <!-- 右下角悬浮首页按钮（阅读页显示） -->
    <router-link
      v-if="isReader"
      to="/"
      class="fixed bottom-6 right-6 z-50 flex h-12 w-12 items-center justify-center rounded-full bg-indigo-600 text-white shadow-lg transition hover:bg-indigo-700 hover:shadow-xl"
      title="返回书架"
    >
      <el-icon :size="22"><HomeFilled /></el-icon>
    </router-link>
  </div>
</template>
