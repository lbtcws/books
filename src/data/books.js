// 从 books_data.json 动态加载书籍数据
import booksData from '../../books_data.json'

// 将 books_data.json 的格式转换为 Vue 组件需要的格式
const img = (prompt, size = 'portrait_16_9') =>
  `https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(
    prompt,
  )}&image_size=${size}`

// 分类图标映射
const categoryIcons = {
  '巴菲特信': '📈',
  '财经': '💰',
  '认知': '🧠',
  '小说': '📖',
}

// 分类 → 默认标签（书籍自身 tags 优先）
const categoryTags = {
  '巴菲特信': ['投资', '巴菲特', '股东信'],
  '财经': ['财经', '商业'],
  '认知': ['认知', '成长'],
  '小说': ['文学', '小说'],
}

// 转换数据格式
export const books = Object.entries(booksData).flatMap(([category, items]) =>
  items.map((item) => ({
    id: item.id,
    title: item.title,
    author: item.author || '未知作者',
    year: item.year || new Date().getFullYear(),
    category,
    format: (item.fileName || '').toLowerCase().split('.').pop(),
    tags: item.tags || categoryTags[category] || [],
    description: item.summary || '',
    file: item.fileName,
    summary: item.summary || '',
    cover: img(
      `Minimalist book cover for "${item.title}" by ${item.author || 'unknown'}, ${category} genre, clean flat design, no text`,
    ),
  })),
)

// 按分类组织的原始数据（供侧边栏使用）
export const booksByCategory = booksData
export { categoryIcons, categoryTags }
