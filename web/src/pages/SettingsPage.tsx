import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function SettingsPage() {
  const [models, setModels] = useState<string[]>([])
  const [model, setModel] = useState(
    () => localStorage.getItem('model') ?? 'llama3',
  )
  const [title, setTitle] = useState('')
  const [lore, setLore] = useState('')
  const [rulesNotes, setRulesNotes] = useState('')
  const [partyText, setPartyText] = useState('')
  const [memoryText, setMemoryText] = useState('')
  const [worldId, setWorldId] = useState<number | null>(null)
  const [gameId, setGameId] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${API_BASE}/health/llm`)
      .then((r) => r.json())
      .then((d) => setModels(d.models ?? []))
      .catch(() => setModels([]))
  }, [])

  useEffect(() => {
    const gid = localStorage.getItem('gameId')
    if (!gid) return
    setGameId(gid)
    async function load() {
      const game = await fetch(`${API_BASE}/games/${gid}`).then((r) => r.json())
      setPartyText(JSON.stringify(game.party ?? [], null, 2))
      setMemoryText(JSON.stringify(game.memory ?? [], null, 2))
      const world = await fetch(`${API_BASE}/worlds/${game.world_id}`).then((r) =>
        r.json(),
      )
      setWorldId(game.world_id)
      setTitle(world.title ?? '')
      setLore(world.lore ?? '')
      setRulesNotes(world.rules_notes ?? '')
    }
    load()
  }, [])

  function saveModel() {
    localStorage.setItem('model', model)
    alert('Model saved')
  }

  async function saveCampaign() {
    if (!gameId || !worldId) return
    try {
      const party = JSON.parse(partyText)
      const memory = JSON.parse(memoryText)
      await fetch(`${API_BASE}/worlds/${worldId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, lore, rules_notes: rulesNotes }),
      })
      await fetch(`${API_BASE}/games/${gameId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ party, memory }),
      })
      alert('Settings saved')
    } catch {
      alert('Invalid JSON in party or memory')
    }
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

      <section className="space-y-2">
        <h2 className="font-semibold">Campaign</h2>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Title"
          className="w-full border p-1 bg-gray-800 text-white"
        />
        <textarea
          value={lore}
          onChange={(e) => setLore(e.target.value)}
          placeholder="Lore"
          className="w-full border p-1 bg-gray-800 text-white"
          rows={4}
        />
        <textarea
          value={rulesNotes}
          onChange={(e) => setRulesNotes(e.target.value)}
          placeholder="Rules notes"
          className="w-full border p-1 bg-gray-800 text-white"
          rows={3}
        />
      </section>

      <section className="space-y-2">
        <h2 className="font-semibold">Party</h2>
        <textarea
          value={partyText}
          onChange={(e) => setPartyText(e.target.value)}
          className="w-full border p-1 bg-gray-800 text-white font-mono"
          rows={6}
        />
      </section>

      <section className="space-y-2">
        <h2 className="font-semibold">Memory</h2>
        <textarea
          value={memoryText}
          onChange={(e) => setMemoryText(e.target.value)}
          className="w-full border p-1 bg-gray-800 text-white font-mono"
          rows={6}
        />
      </section>

      <button
        onClick={saveCampaign}
        className="rounded bg-blue-600 px-2 py-1 text-white"
      >
        Save Campaign
      </button>
    </div>
  )
}

