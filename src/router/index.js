import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ReaderView from '../views/ReaderView.vue'

// 使用 hash 历史模式：GitHub Pages 无需配置 404 重定向即可正常刷新/直达
const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/read/:id', name: 'reader', component: ReaderView, props: true },
  ],
})

export default router
