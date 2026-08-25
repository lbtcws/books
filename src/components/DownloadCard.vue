<script setup>
import { computed } from 'vue'
import { Download } from '@element-plus/icons-vue'

const props = defineProps({
  book: { type: Object, required: true },
  fileUrl: { type: String, required: true },
})

const fileExt = computed(() => {
  return props.book.file.split('.').pop().toUpperCase()
})

const formatDescription = computed(() => {
  const ext = fileExt.value
  if (ext === 'EPUB') return 'EPUB 格式建议下载后使用阅读器打开'
  if (ext === 'MOBI') return 'MOBI 格式建议下载后使用 Kindle 阅读器打开'
  if (ext === 'RAR' || ext === 'ZIP') return '压缩包格式，请下载后解压查看'
  return `${ext} 格式暂不支持在线预览，请下载后查看`
})
</script>

<template>
  <div class="flex h-full flex-col items-center justify-center bg-slate-50 p-8">
    <div class="flex flex-col items-center gap-6 text-center">
      <!-- 图标 -->
      <div class="flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg">
        <el-icon :size="48" class="text-white"><Download /></el-icon>
      </div>

      <!-- 标题 -->
      <div>
        <h3 class="text-2xl font-semibold text-slate-800">{{ book.title }}</h3>
        <p class="mt-2 text-sm text-slate-500">{{ book.author }}</p>
      </div>

      <!-- 说明 -->
      <p class="max-w-md text-slate-600">{{ formatDescription }}</p>

      <!-- 下载按钮 -->
      <a :href="fileUrl" download class="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 px-8 py-3 font-semibold text-white shadow-lg transition hover:-translate-y-0.5 hover:shadow-xl">
        <el-icon :size="20"><Download /></el-icon>
        <span>立即下载</span>
      </a>

      <!-- 返回链接 -->
      <router-link to="/" class="mt-4 text-sm text-slate-500 hover:text-indigo-600">
        返回书架
      </router-link>
    </div>
  </div>
</template>
