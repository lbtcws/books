import { reactive } from 'vue'

export interface AIAnswer {
  enabled: boolean
  answer: string
  sources?: AISource[]
  error?: string
}

export interface AISource {
  title: string
  locator?: string
}

export interface AIProvider {
  /** 当前模式是否启用 AI */
  readonly enabled: boolean
  /** 对文本做总结 */
  summary(text: string, context?: string): Promise<AIAnswer>
  /** 知识库问答 */
  chat(question: string, context?: string): Promise<AIAnswer>
}

export interface AIConfig {
  baseUrl: string
  apiKey: string
  model: string
}

export const AI_CONFIG_KEY = 'books-ai-config'
const DEFAULT_CONFIG: AIConfig = {
  baseUrl: 'https://api.openai.com/v1',
  apiKey: '',
  model: '',
}

function loadConfig(): AIConfig {
  try {
    return { ...DEFAULT_CONFIG, ...JSON.parse(localStorage.getItem(AI_CONFIG_KEY) || '{}') }
  } catch {
    return { ...DEFAULT_CONFIG }
  }
}

export const aiConfig = reactive<AIConfig>(loadConfig())

export function saveAIConfig(config: AIConfig) {
  Object.assign(aiConfig, config)
  localStorage.setItem(AI_CONFIG_KEY, JSON.stringify(aiConfig))
}

export function clearAIConfig() {
  saveAIConfig({ ...DEFAULT_CONFIG })
}

const DISABLED_ANSWER: AIAnswer = {
  enabled: false,
  answer: '当前为 Static Mode（Github Pages），AI 功能未启用。本地运行 docker compose 启动 AI 服务后，将 VITE_MODE=ai 重新构建即可开启。',
}

export class StaticAIProvider implements AIProvider {
  readonly enabled = false

  async summary(_text: string, _context?: string): Promise<AIAnswer> {
    return DISABLED_ANSWER
  }

  async chat(_question: string, _context?: string): Promise<AIAnswer> {
    return DISABLED_ANSWER
  }
}

export class RemoteAIProvider implements AIProvider {
  readonly enabled = true
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/+$/, '')
  }

  private async post(path: string, body: unknown): Promise<AIAnswer> {
    try {
      const res = await fetch(`${this.baseUrl}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      return {
        enabled: true,
        answer: data.answer ?? '',
        sources: data.sources ?? [],
      }
    } catch (e) {
      return {
        enabled: true,
        answer: '',
        error: `AI 服务不可用（${this.baseUrl}）：${(e as Error).message}。请确认 backend 已通过 docker compose 启动。`,
      }
    }
  }

  summary(text: string, context = ''): Promise<AIAnswer> {
    return this.post('/api/rag/summary', { text: context ? `${context}\n\n${text}` : text })
  }

  chat(question: string, context = ''): Promise<AIAnswer> {
    return this.post('/api/rag/chat', { question, context })
  }
}

class UserAIProvider implements AIProvider {
  get enabled() {
    return Boolean(aiConfig.baseUrl.trim() && aiConfig.apiKey.trim() && aiConfig.model.trim())
  }

  private async complete(messages: Array<{ role: string; content: string }>): Promise<AIAnswer> {
    if (!this.enabled) return DISABLED_ANSWER
    try {
      const baseUrl = aiConfig.baseUrl.trim().replace(/\/+$/, '')
      const res = await fetch(`${baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${aiConfig.apiKey.trim()}`,
        },
        body: JSON.stringify({ model: aiConfig.model.trim(), messages, temperature: 0.3 }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data?.error?.message || `HTTP ${res.status}`)
      return { enabled: true, answer: data?.choices?.[0]?.message?.content || '（无回答）' }
    } catch (e) {
      return { enabled: true, answer: '', error: `大模型请求失败：${(e as Error).message}` }
    }
  }

  summary(text: string, context = '') {
    return this.complete([
      { role: 'system', content: '你是用户的私人阅读助手。请基于当前书籍上下文，用中文给出准确、结构化的回答。资料不足时明确说明，不要编造。' },
      { role: 'user', content: `${context}\n\n请总结以下内容：\n${text.slice(0, 16000)}` },
    ])
  }

  chat(question: string, context = '') {
    return this.complete([
      { role: 'system', content: '你是用户的私人阅读助手。当前对话只围绕用户正在阅读的这本书展开。请用中文回答，优先引用或解释书籍上下文，资料不足时明确说明。' },
      { role: 'user', content: `${context}\n\n用户问题：${question}` },
    ])
  }
}

// 根据环境变量选择实现：默认 static，保证 Github Pages 零后端可运行
export function createAIProvider(): AIProvider {
  const mode = import.meta.env.VITE_MODE || 'static'
  const api = import.meta.env.VITE_AI_API
  if (aiConfig.baseUrl.trim() && aiConfig.apiKey.trim() && aiConfig.model.trim()) return new UserAIProvider()
  if (mode === 'ai' && api) return new RemoteAIProvider(api)
  return new UserAIProvider()
}

export const aiProvider: AIProvider = createAIProvider()
