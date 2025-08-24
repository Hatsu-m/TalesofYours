import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL ?? ''

interface ParsedWorld {
  id: string
  title: string
  ruleset: string
  end_goal: string
  lore: string
  locations: unknown[]
  npcs: unknown[]
  factions: unknown[]
  items: unknown[]
  rules_notes?: string | null
}

export default function WorldEditorPage() {
  const navigate = useNavigate()
  const [markdown, setMarkdown] = useState(
    `---\nid: demo\ntitle: Demo World\nruleset: custom_d6\nend_goal: Have fun\n---\n\n## Lore\nDescribe your world.\n`
  )
  const [preview, setPreview] = useState<ParsedWorld | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`${API_BASE}/worlds/validate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content: markdown }),
          signal: controller.signal,
        })
        if (!res.ok) {
          const data = await res.json()
          throw new Error(data.detail ?? 'invalid markdown')
        }
        const data = await res.json()
        setPreview(data)
        setError(null)
      } catch (err) {
        setPreview(null)
        setError((err as Error).message)
      }
    }, 300)
    return () => {
      controller.abort()
      clearTimeout(timer)
    }
  }, [markdown])

  async function handleSave() {
    const res = await fetch(`${API_BASE}/worlds/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: markdown }),
    })
    if (!res.ok) return
    const { id: worldId } = await res.json()
    const res2 = await fetch(`${API_BASE}/games`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ world_id: worldId }),
    })
    if (!res2.ok) return
    const { id: gameId } = await res2.json()
    navigate(`/play/${gameId}`)
  }

  return (
    <div className="flex h-full flex-col bg-gray-100 dark:bg-gray-900 dark:text-gray-100">
      <div className="flex flex-1 flex-col md:flex-row">
        <textarea
          value={markdown}
          onChange={(e) => setMarkdown(e.target.value)}
          className="h-64 flex-1 border border-gray-700 bg-white p-2 font-mono dark:bg-gray-800 md:h-auto"
        />
        <div className="flex-1 overflow-auto border border-gray-700 p-2">
          {error && <p className="text-red-500">{error}</p>}
          {preview && <pre className="text-xs">{JSON.stringify(preview, null, 2)}</pre>}
        </div>
      </div>
      <div className="border-t border-gray-700 p-2 text-right">
        <button
          onClick={handleSave}
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          Save &amp; Play
        </button>
      </div>
    </div>
  )
}
