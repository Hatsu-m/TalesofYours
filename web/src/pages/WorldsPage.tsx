import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

interface WorldSummary {
  id: number
  title: string
  ruleset: string
}

interface SavedGame {
  id: number
  world_id: number
}

export default function WorldsPage() {
  const navigate = useNavigate()
  const [worlds, setWorlds] = useState<WorldSummary[]>([])
  const [saves, setSaves] = useState<Record<number, number[]>>({})

  async function fetchWorlds() {
    try {
      const res = await fetch(`${API_BASE}/worlds`)
      const data = (await res.json()) as WorldSummary[]
      setWorlds(data)
    } catch {
      setWorlds([])
    }
  }

  async function fetchSaves() {
    try {
      const res = await fetch(`${API_BASE}/games`)
      const data = (await res.json()) as SavedGame[]
      const grouped: Record<number, number[]> = {}
      for (const g of data) {
        grouped[g.world_id] = grouped[g.world_id] || []
        grouped[g.world_id].push(g.id)
      }
      setSaves(grouped)
    } catch {
      setSaves({})
    }
  }

  async function handleRefresh() {
    await fetchWorlds()
    await fetchSaves()
  }

  useEffect(() => {
    fetchWorlds()
    fetchSaves()
  }, [])

  async function importFile(file: File) {
    const content = await file.text()
    const res = await fetch(`${API_BASE}/worlds/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    })
    if (!res.ok) {
      const message = await res.text()
      alert(`Import failed: ${message}`)
      return
    }
    await fetchWorlds()
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      await importFile(file)
    } catch (err) {
      console.error(err)
      const msg = err instanceof Error ? err.message : String(err)
      alert(`Import failed: ${msg}`)
    } finally {
      e.target.value = ''
    }
  }

  function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0]
    if (file) {
      importFile(file).catch((err) => {
        console.error(err)
        const msg = err instanceof Error ? err.message : String(err)
        alert(`Import failed: ${msg}`)
      })
    }
  }

  function handleDragOver(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault()
  }

  async function handlePlay(worldId: number) {
    const res = await fetch(`${API_BASE}/games`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ world_id: worldId }),
    })
    if (!res.ok) return
    const { id } = await res.json()
    navigate(`/play/${id}`)
  }

  async function handleLoad(gameId: number) {
    const res = await fetch(`${API_BASE}/games/${gameId}/load`, {
      method: 'POST',
    })
    if (res.ok) {
      navigate(`/play/${gameId}`)
    }
  }

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      className="flex h-full flex-col items-center gap-4 bg-gray-100 p-4 dark:bg-gray-900 dark:text-gray-100"
    >
      <h1 className="text-2xl font-bold">Worlds</h1>
      <input
        type="file"
        accept=".md,text/markdown"
        onChange={handleUpload}
        className="w-full max-w-md"
      />
      <button onClick={handleRefresh} className="text-blue-500 underline">
        Refresh
      </button>
      <ul className="w-full max-w-md flex-1 overflow-auto">
        {worlds.map((w) => (
          <li key={w.id} className="border-b border-gray-700 p-2">
            <button
              onClick={() => handlePlay(w.id)}
              className="w-full text-left hover:underline"
            >
              {w.title}{' '}
              <span className="text-sm text-gray-500">({w.ruleset})</span>
            </button>
            {saves[w.id] && (
              <ul className="mt-1 ml-2 space-y-1 text-sm">
                {saves[w.id].map((sid) => (
                  <li key={sid}>
                    <button
                      onClick={() => handleLoad(sid)}
                      className="text-left text-blue-500 hover:underline"
                    >
                      Load save #{sid}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
      <Link to="/" className="text-blue-500 underline">
        Home
      </Link>
    </div>
  )
}
