export const themes = {
  light: { color: '#333', background: '#fdfdf8', scrollbar: '#c4c8c2' },
  sepia: { color: '#5b4636', background: '#f4ecd8', scrollbar: '#c2ae8b' },
  dark: { color: '#c9d1d9', background: '#1e1e1e', scrollbar: '#626a73' },
}

export function applyAppTheme(name = 'light') {
  const theme = themes[name] || themes.light
  const themeName = themes[name] ? name : 'light'
  const root = document.documentElement
  root.style.setProperty('--app-background', theme.background)
  root.style.setProperty('--app-foreground', theme.color)
  root.style.setProperty('--app-scrollbar', theme.scrollbar)
  root.style.setProperty('--el-bg-color', theme.background)
  root.style.setProperty('--el-bg-color-page', theme.background)
  root.style.setProperty('--el-bg-color-overlay', theme.background)
  root.style.setProperty('--el-fill-color-blank', theme.background)
  document.body.style.backgroundColor = theme.background
  document.body.style.color = theme.color
  try {
    const settings = JSON.parse(localStorage.getItem('books-reader-epub-settings') || '{}')
    localStorage.setItem('books-reader-epub-settings', JSON.stringify({ ...settings, theme: themeName }))
  } catch {
    localStorage.setItem('books-reader-epub-settings', JSON.stringify({ theme: themeName }))
  }
  return theme
}

export function loadSavedTheme() {
  try {
    return JSON.parse(localStorage.getItem('books-reader-epub-settings') || '{}').theme || 'light'
  } catch {
    return 'light'
  }
}
