import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL ?? ''

interface WorldSummary {
  id: number
  title: string
  ruleset: string
}

export default function WorldsPage() {
  const [worlds, setWorlds] = useState<WorldSummary[]>([])

  useEffect(() => {
    fetch(`${API_BASE}/worlds`)
      .then((r) => r.json())
      .then((data) => setWorlds(data as WorldSummary[]))
      .catch(() => setWorlds([]))
  }, [])

  return (
    <div className="flex h-full flex-col items-center gap-4 bg-gray-100 p-4 dark:bg-gray-900 dark:text-gray-100">
      <h1 className="text-2xl font-bold">Worlds</h1>
      <ul className="w-full max-w-md flex-1 overflow-auto">
        {worlds.map((w) => (
          <li key={w.id} className="border-b border-gray-700 p-2">
            {w.title} <span className="text-sm text-gray-500">({w.ruleset})</span>
          </li>
        ))}
      </ul>
      <Link
        to="/worlds/new"
        className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        New World
      </Link>
      <Link to="/" className="text-blue-500 underline">
        Back
      </Link>
    </div>
  )
}
