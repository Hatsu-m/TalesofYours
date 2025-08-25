import { useEffect, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

type WorldData = {
  lore: string
  rules_notes?: string
  npcs: { name: string; description: string }[]
}

type PartyMember = {
  id: number | string
  name: string
  stats?: Record<string, number>
  inventory?: string[]
}

export default function SettingsPage() {
  const [models, setModels] = useState<string[]>([])
  const [model, setModel] = useState(
    () => localStorage.getItem('model') ?? 'llama3',
  )

  // world editing
  const [worldId, setWorldId] = useState('')
  const [world, setWorld] = useState<WorldData | null>(null)

  // party editing
  const [gameId, setGameId] = useState('')
  const [party, setParty] = useState<PartyMember[]>([])

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

  async function loadWorld() {
    if (!worldId) return
    const data = await fetch(`${API_BASE}/worlds/${worldId}`).then((r) => r.json())
    setWorld(data)
  }

  async function saveWorld() {
    if (!worldId) return
    await fetch(`${API_BASE}/worlds/${worldId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lore: world.lore,
        rules_notes: world.rules_notes,
        npcs: world.npcs,
      }),
    })
    alert('World saved')
  }

  async function loadGame() {
    if (!gameId) return
    const data = await fetch(`${API_BASE}/games/${gameId}`).then((r) => r.json())
    setParty(data.party ?? [])
  }

  async function saveMember(idx: number) {
    const member = party[idx]
    await fetch(`${API_BASE}/games/${gameId}/party/${member.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(member),
    })
  }

  return (
    <div className="space-y-6 p-4">
      <h1 className="text-xl font-bold">Settings</h1>

      <section>
        <h2 className="font-semibold">Model</h2>
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="border p-1"
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
        <h2 className="font-semibold">World Editor</h2>
        <div className="space-x-2">
          <input
            value={worldId}
            onChange={(e) => setWorldId(e.target.value)}
            placeholder="World ID"
            className="w-24 border p-1"
          />
          <button
            onClick={loadWorld}
            className="rounded bg-gray-700 px-2 py-1 text-white"
          >
            Load
          </button>
          {world && (
            <button
              onClick={saveWorld}
              className="rounded bg-blue-600 px-2 py-1 text-white"
            >
              Save
            </button>
          )}
        </div>
        {world && (
          <div className="space-y-2">
            <div>
              <label className="block text-sm font-medium">Lore</label>
              <textarea
                value={world.lore}
                onChange={(e) => setWorld({ ...world, lore: e.target.value })}
                className="h-24 w-full border p-1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Rules Notes</label>
              <textarea
                value={world.rules_notes ?? ''}
                onChange={(e) =>
                  setWorld({ ...world, rules_notes: e.target.value })
                }
                className="h-24 w-full border p-1"
              />
            </div>
          </div>
        )}
      </section>

      <section className="space-y-2">
        <h2 className="font-semibold">Party Editor</h2>
        <div className="space-x-2">
          <input
            value={gameId}
            onChange={(e) => setGameId(e.target.value)}
            placeholder="Game ID"
            className="w-24 border p-1"
          />
          <button
            onClick={loadGame}
            className="rounded bg-gray-700 px-2 py-1 text-white"
          >
            Load
          </button>
        </div>
        {party.map((m, idx) => (
          <div key={m.id} className="rounded border p-2">
            <div className="flex items-center gap-2">
              <input
                value={m.name}
                onChange={(e) => {
                  const copy = [...party]
                  copy[idx] = { ...copy[idx], name: e.target.value }
                  setParty(copy)
                }}
                className="border p-1"
              />
              <button
                onClick={() => saveMember(idx)}
                className="rounded bg-blue-600 px-2 py-1 text-white"
              >
                Save
              </button>
            </div>
            {m.stats && (
              <div className="mt-2 text-sm">
                HP:{' '}
                <input
                  type="number"
                  value={m.stats.hp ?? 0}
                  onChange={(e) => {
                    const copy = [...party]
                    copy[idx] = {
                      ...copy[idx],
                      stats: { ...copy[idx].stats, hp: Number(e.target.value) },
                    }
                    setParty(copy)
                  }}
                  className="w-16 border p-1"
                />
              </div>
            )}
            {m.inventory && (
              <div className="mt-2 text-sm">
                Inventory (comma separated):
                <input
                  value={m.inventory.join(', ')}
                  onChange={(e) => {
                    const items = e.target.value
                      .split(',')
                      .map((s) => s.trim())
                      .filter(Boolean)
                    const copy = [...party]
                    copy[idx] = { ...copy[idx], inventory: items }
                    setParty(copy)
                  }}
                  className="ml-2 w-full border p-1"
                />
              </div>
            )}
          </div>
        ))}
      </section>
    </div>
  )
}
