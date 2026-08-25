// 全局加载 pdf.js 并挂载到 window
import * as pdfjsLib from './pdfjs/pdf.min.mjs'

// 挂载到全局（PdfViewer.vue 会自行配置 worker）
window.pdfjsLib = pdfjsLib
