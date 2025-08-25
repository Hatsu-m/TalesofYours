import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

interface WorldSummary {
  id: number
  title: string
  ruleset: string
}

export default function WorldsPage() {
  const navigate = useNavigate()
  const [worlds, setWorlds] = useState<WorldSummary[]>([])

  async function fetchWorlds() {
    fetch(`${API_BASE}/worlds`)
      .then((r) => r.json())
      .then((data) => setWorlds(data as WorldSummary[]))
      .catch(() => setWorlds([]))
  }

  useEffect(() => {
    fetchWorlds()
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
      alert('Import failed')
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
        alert('Import failed')
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
          </li>
        ))}
      </ul>
      <Link to="/" className="text-blue-500 underline">
        Home
      </Link>
    </div>
  )
}
