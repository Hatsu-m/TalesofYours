import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL ?? window.location.origin

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
    `---\nid: demo\ntitle: Demo World\nruleset: custom_d6\nend_goal: Have fun\n---\n\n## Lore\nDescribe your world.\n`,
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
        const msg = err instanceof Error ? err.message : String(err)
        if (msg === 'Failed to fetch') {
          setError(`Cannot reach server at ${API_BASE}. Is it running?`)
        } else {
          setError(msg)
        }
      }
    }, 300)
    return () => {
      controller.abort()
      clearTimeout(timer)
    }
  }, [markdown])

  async function handleSave() {
    try {
      const res = await fetch(`${API_BASE}/worlds/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: markdown }),
      })
      if (!res.ok) {
        const msg = await res.text()
        throw new Error(msg || 'world import failed')
      }
      const { id: worldId } = await res.json()
      const res2 = await fetch(`${API_BASE}/games`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ world_id: worldId }),
      })
      if (!res2.ok) {
        const msg = await res2.text()
        throw new Error(msg || 'game creation failed')
      }
      const { id: gameId } = await res2.json()
      navigate(`/play/${gameId}`)
    } catch (err) {
      console.error(err)
      const msg = err instanceof Error ? err.message : String(err)
      if (msg === 'Failed to fetch') {
        alert(`Import failed: could not reach server at ${API_BASE}. Is it running?`)
      } else {
        alert(`Import failed: ${msg}`)
      }
    }
  }

  return (
    <div className="relative flex h-full flex-col bg-gray-100 dark:bg-gray-900 dark:text-gray-100">
      <Link
        to="/"
        className="absolute left-2 top-2 rounded bg-blue-600 px-2 py-1 text-white hover:bg-blue-700"
      >
        Home
      </Link>
      <div className="flex flex-1 flex-col md:flex-row">
        <textarea
          value={markdown}
          onChange={(e) => setMarkdown(e.target.value)}
          className="h-64 flex-1 border border-gray-700 bg-white p-2 font-mono dark:bg-gray-800 md:h-auto"
        />
        <div className="flex-1 overflow-auto border border-gray-700 p-2">
          {error && <p className="text-red-500">{error}</p>}
          {preview && (
            <pre className="text-xs">{JSON.stringify(preview, null, 2)}</pre>
          )}
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
