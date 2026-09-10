<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBooksStore } from '../stores/books'
import { Search, ArrowRight, View, Download, Setting } from '@element-plus/icons-vue'
import { applyAppTheme, loadSavedTheme, themes } from '../services/theme'
import { aiConfig, aiProvider, saveAIConfig } from '../services/ai/AIProvider'

const store = useBooksStore()
const router = useRouter()

// 搜索关键词
const searchQuery = ref('')
const selectedTheme = ref(loadSavedTheme())
const showAISettings = ref(false)
const aiDraft = ref({ ...aiConfig })
const aiConfigured = computed(() => aiProvider.enabled)

function setTheme(name) {
  selectedTheme.value = name
  applyAppTheme(name)
}

function openAISettings() {
  aiDraft.value = { ...aiConfig }
  showAISettings.value = true
}

function saveAISettings() {
  saveAIConfig({ ...aiDraft.value })
  showAISettings.value = false
}

// 分类展开状态
const expandedCategories = ref(Object.keys(store.byCategory).reduce((acc, cat) => {
  acc[cat] = true
  return acc
}, {}))

// 过滤后的书籍（标题 / 作者 / 标签 / 简介）
const filteredBooks = computed(() => {
  if (!searchQuery.value.trim()) return store.byCategory
  const query = searchQuery.value.toLowerCase()
  const result = {}
  for (const [category, books] of Object.entries(store.byCategory)) {
    const filtered = books.filter(book =>
      book.title.toLowerCase().includes(query) ||
      book.author?.toLowerCase().includes(query) ||
      (book.tags || store.categoryTags[category] || []).some((t) => t.toLowerCase().includes(query)) ||
      (book.summary || '').toLowerCase().includes(query)
    )
    if (filtered.length > 0) {
      result[category] = filtered
    }
  }
  return result
})

// 切换分类展开
function toggleCategory(category) {
  expandedCategories.value[category] = !expandedCategories.value[category]
}

// 打开书籍
function openBook(book) {
  router.push({ name: 'reader', params: { id: book.id } })
}

const readableFormats = new Set(['pdf', 'epub', 'mobi', 'md', 'txt'])

function getFileExtension(book) {
  return (book.fileName || '').toLowerCase().split('.').pop()
}

function canRead(book) {
  return readableFormats.has(getFileExtension(book))
}

function fileExtension(book) {
  const extension = getFileExtension(book)
  return extension ? `.${extension.toUpperCase()}` : ''
}
</script>

<template>
  <div class="flex h-[calc(100vh-3.5rem)]">
    <!-- 侧边栏 -->
    <aside class="flex w-80 flex-col border-r border-slate-200 bg-white">
      <!-- 搜索框 -->
      <div class="border-b border-slate-200 p-4">
        <div class="flex items-center gap-2">
          <el-input
            v-model="searchQuery"
            placeholder="搜索书籍..."
            :prefix-icon="Search"
            clearable
            size="large"
          />
          <el-dropdown @command="setTheme">
            <el-button size="large" title="设置背景色">
              背景
              <span class="ml-1 inline-block h-3 w-3 rounded-full border border-slate-300" :style="{ background: themes[selectedTheme].background }" />
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="light">白色</el-dropdown-item>
                <el-dropdown-item command="sepia">护眼</el-dropdown-item>
                <el-dropdown-item command="dark">深色</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button
            size="large"
            circle
            :icon="Setting"
            :title="aiConfigured ? '设置（大模型已配置）' : '设置大模型'"
            aria-label="设置"
            class="!border-[var(--app-foreground)] !bg-[var(--app-background)] !text-[var(--app-foreground)]"
            @click="openAISettings"
          />
        </div>
      </div>

      <!-- 书籍列表 -->
      <div class="flex-1 overflow-y-auto p-4">
        <div v-for="(books, category) in filteredBooks" :key="category" class="mb-6">
          <!-- 分类标题 -->
          <div
            class="mb-3 flex cursor-pointer items-center gap-2 rounded-lg bg-slate-100 px-4 py-3 transition hover:bg-slate-200"
            @click="toggleCategory(category)"
          >
            <span class="text-xl">{{ store.categoryIcons[category] || '📚' }}</span>
            <span class="flex-1 font-semibold text-slate-700">{{ category }}</span>
            <span class="rounded-full bg-indigo-500 px-2 py-0.5 text-xs font-semibold text-white">
              {{ books.length }}
            </span>
            <el-icon class="text-slate-400 transition-transform" :class="{ 'rotate-90': expandedCategories[category] }">
              <ArrowRight />
            </el-icon>
          </div>

          <!-- 书籍列表 -->
          <div v-show="expandedCategories[category]" class="space-y-1">
            <div
              v-for="book in books"
              :key="book.id"
              class="flex cursor-pointer items-center gap-2 rounded-lg px-4 py-2.5 text-sm text-slate-600 transition hover:bg-indigo-50 hover:text-indigo-600"
              @click="openBook(book)"
            >
              <el-icon
                class="shrink-0"
                :class="canRead(book) ? 'text-indigo-500' : 'text-slate-400'"
                :title="canRead(book) ? '在线查看' : '下载后查看'"
              >
                <component :is="canRead(book) ? View : Download" />
              </el-icon>
              <span class="flex-1 truncate">{{ book.title }}</span>
              <span class="shrink-0 text-xs uppercase text-slate-400">{{ fileExtension(book) }}</span>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="Object.keys(filteredBooks).length === 0" class="flex flex-col items-center justify-center py-12 text-slate-400">
          <el-icon :size="48"><Search /></el-icon>
          <p class="mt-4 text-sm">未找到匹配的书籍</p>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="flex-1 overflow-y-auto bg-slate-50">
      <div class="mx-auto max-w-5xl px-8 py-8">
        <!-- 欢迎信息 -->
        <div class="mb-8 text-center">
          <h1 class="text-3xl font-bold text-slate-800">欢迎来到数字图书馆</h1>
          <p class="mt-2 text-slate-600">共 {{ store.totalBooks }} 本藏书，{{ store.totalCategories }} 个分类</p>
        </div>

        <!-- 特性卡片 -->
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div class="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
            <div class="mb-3 text-4xl">📖</div>
            <h3 class="mb-2 font-semibold text-slate-800">经典小说</h3>
            <p class="text-sm text-slate-500">中外文学名著与热门小说</p>
          </div>
          <div class="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
            <div class="mb-3 text-4xl">📊</div>
            <h3 class="mb-2 font-semibold text-slate-800">投资理财</h3>
            <p class="text-sm text-slate-500">巴菲特、芒格等大师经典</p>
          </div>
          <div class="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
            <div class="mb-3 text-4xl">🧠</div>
            <h3 class="mb-2 font-semibold text-slate-800">认知成长</h3>
            <p class="text-sm text-slate-500">思维模型与决策智慧</p>
          </div>
          <div class="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
            <div class="mb-3 text-4xl">📈</div>
            <h3 class="mb-2 font-semibold text-slate-800">财经经典</h3>
            <p class="text-sm text-slate-500">经济学与商业洞察</p>
          </div>
        </div>

        <!-- 使用说明 -->
        <div class="mt-12 rounded-xl border border-slate-200 bg-white p-6">
          <h2 class="mb-4 text-xl font-semibold text-slate-800">使用说明</h2>
          <ul class="space-y-2 text-slate-600">
            <li class="flex items-start gap-2">
              <span class="text-indigo-500">•</span>
              <span><strong>PDF 文件</strong>：支持在线连续滚动阅读，可缩放、翻页</span>
            </li>
            <li class="flex items-start gap-2">
              <span class="text-indigo-500">•</span>
              <span><strong>Markdown 文件</strong>：支持在线渲染阅读</span>
            </li>
            <li class="flex items-start gap-2">
              <span class="text-indigo-500">•</span>
              <span><strong>TXT 文件</strong>：支持在线纯文本阅读</span>
            </li>
            <li class="flex items-start gap-2">
              <span class="text-indigo-500">•</span>
              <span><strong>EPUB 文件</strong>：支持在线翻页阅读，含目录、字体、背景、书签与阅读进度</span>
            </li>
            <li class="flex items-start gap-2">
              <span class="text-indigo-500">•</span>
              <span><strong>MOBI 文件</strong>：支持在线翻页与章节阅读，含目录、字体、背景、书签与阅读进度</span>
            </li>
            <li class="flex items-start gap-2">
              <span class="text-indigo-500">•</span>
              <span><strong>其他格式</strong>（RAR、ZIP 等）：请下载后使用相应阅读器打开</span>
            </li>
          </ul>
        </div>
      </div>
    </main>

    <el-dialog v-model="showAISettings" title="大模型配置" width="min(92vw, 560px)">
      <div class="space-y-4">
        <p class="text-sm text-slate-500">
          配置会保存在当前浏览器中。阅读页面的 AI 助手会直接调用你填写的 OpenAI 兼容接口。
        </p>
        <el-form label-position="top">
          <el-form-item label="Base URL">
            <el-input v-model="aiDraft.baseUrl" placeholder="https://api.openai.com/v1" />
          </el-form-item>
          <el-form-item label="API Key">
            <el-input v-model="aiDraft.apiKey" type="password" show-password placeholder="sk-..." />
          </el-form-item>
          <el-form-item label="模型 ID">
            <el-input v-model="aiDraft.model" placeholder="例如：gpt-4o-mini、deepseek-chat" />
          </el-form-item>
        </el-form>
        <p class="text-xs text-slate-400">
          Base URL 应指向兼容接口的根路径，例如以 `/v1` 结尾；API Key 仅用于浏览器直接请求，不会上传到本项目服务器。
        </p>
      </div>
      <template #footer>
        <el-button @click="showAISettings = false">取消</el-button>
        <el-button type="primary" @click="saveAISettings">保存配置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.rotate-90 {
  transform: rotate(90deg);
}
</style>
