// AI Provider 抽象层：前端不直接绑定任何 AI 后端。
// Static Mode（Github Pages）下 StaticAIProvider 返回 disabled；
// AI Mode 下 RemoteAIProvider 调用本地 FastAPI。

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
  summary(text: string): Promise<AIAnswer>
  /** 知识库问答 */
  chat(question: string): Promise<AIAnswer>
}

const DISABLED_ANSWER: AIAnswer = {
  enabled: false,
  answer: '当前为 Static Mode（Github Pages），AI 功能未启用。本地运行 docker compose 启动 AI 服务后，将 VITE_MODE=ai 重新构建即可开启。',
}

export class StaticAIProvider implements AIProvider {
  readonly enabled = false

  async summary(_text: string): Promise<AIAnswer> {
    return DISABLED_ANSWER
  }

  async chat(_question: string): Promise<AIAnswer> {
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

  summary(text: string): Promise<AIAnswer> {
    return this.post('/api/rag/summary', { text })
  }

  chat(question: string): Promise<AIAnswer> {
    return this.post('/api/rag/chat', { question })
  }
}

// 根据环境变量选择实现：默认 static，保证 Github Pages 零后端可运行
export function createAIProvider(): AIProvider {
  const mode = import.meta.env.VITE_MODE || 'static'
  const api = import.meta.env.VITE_AI_API
  if (mode === 'ai' && api) return new RemoteAIProvider(api)
  return new StaticAIProvider()
}

export const aiProvider: AIProvider = createAIProvider()
