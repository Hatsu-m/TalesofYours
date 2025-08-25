import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function SettingsPage() {
  const [models, setModels] = useState<string[]>([])
  const [model, setModel] = useState(
    () => localStorage.getItem('model') ?? 'llama3',
  )

  useEffect(() => {
    fetch(`${API_BASE}/health/llm`)
      .then((r) => r.json())
      .then((d) => setModels(d.models ?? []))
      .catch(() => setModels([]))
  }, [])

  function saveModel() {
    localStorage.setItem('model', model)
    alert('Model saved')
  }

  return (
    <div className="space-y-6 p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">Settings</h1>
        <Link to="/" className="text-blue-500 underline">
          Home
        </Link>
      </div>

      <section>
        <h2 className="font-semibold">Model</h2>
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="border p-1 bg-gray-800 text-white"
        >
          {models.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
        <button
          onClick={saveModel}
          className="ml-2 rounded bg-blue-600 px-2 py-1 text-white"
        >
          Save
        </button>
      </section>
    </div>
  )
}

