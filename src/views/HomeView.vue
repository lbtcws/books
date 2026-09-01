<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBooksStore } from '../stores/books'
import { Search, ArrowRight } from '@element-plus/icons-vue'

const store = useBooksStore()
const router = useRouter()

// 搜索关键词
const searchQuery = ref('')

// 分类展开状态
const expandedCategories = ref(Object.keys(store.byCategory).reduce((acc, cat) => {
  acc[cat] = true
  return acc
}, {}))

// 过滤后的书籍
const filteredBooks = computed(() => {
  if (!searchQuery.value.trim()) return store.byCategory
  const query = searchQuery.value.toLowerCase()
  const result = {}
  for (const [category, books] of Object.entries(store.byCategory)) {
    const filtered = books.filter(book => 
      book.title.toLowerCase().includes(query) ||
      book.author?.toLowerCase().includes(query)
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
</script>

<template>
  <div class="flex h-[calc(100vh-3.5rem)]">
    <!-- 侧边栏 -->
    <aside class="flex w-80 flex-col border-r border-slate-200 bg-white">
      <!-- 搜索框 -->
      <div class="border-b border-slate-200 p-4">
        <el-input
          v-model="searchQuery"
          placeholder="搜索书籍..."
          :prefix-icon="Search"
          clearable
          size="large"
        />
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
              <span class="text-base">📄</span>
              <span class="flex-1 truncate">{{ book.title }}</span>
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
              <span><strong>其他格式</strong>（EPUB、MOBI 等）：请下载后使用相应阅读器打开</span>
            </li>
          </ul>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.rotate-90 {
  transform: rotate(90deg);
}
</style>
