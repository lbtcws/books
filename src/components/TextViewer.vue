<script setup>
import { ref, onMounted } from 'vue'
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
    content.value = text
    loading.value = false
  } catch (e) {
    console.error('[TextViewer] load failed', e)
    error.value = e.message || '文本加载失败'
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
      <pre class="whitespace-pre-wrap break-words font-sans text-base leading-relaxed text-slate-700">{{ content }}</pre>
    </div>
  </div>
</template>

<style scoped>
pre {
  font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', system-ui, -apple-system, sans-serif;
}
</style>
