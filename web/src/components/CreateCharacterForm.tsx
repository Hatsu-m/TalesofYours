import React, { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface NewCharacter {
  id: number | string
  name: string
  background?: string
  traits?: string
  stats: Record<string, number>
  inventory: string[]
}

interface Props {
  gameId: string
  onCreated: (character: NewCharacter) => void
}

export default function CreateCharacterForm({ gameId, onCreated }: Props) {
  const [name, setName] = useState('')
  const [background, setBackground] = useState('')
  const [traits, setTraits] = useState('')
  const [hp, setHp] = useState(10)
  const [strength, setStrength] = useState(0)
  const [defense, setDefense] = useState(0)
  const [inventory, setInventory] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const character: NewCharacter = {
      id: 1,
      name,
      background: background || undefined,
      traits: traits || undefined,
      stats: { hp, strength, defense },
      inventory: inventory
        .split(',')
        .map((i) => i.trim())
        .filter((i) => i.length > 0),
    }

    await fetch(`${API_BASE}/games/${gameId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ party: [character] }),
    })

    onCreated(character)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-2 text-sm">
      <div>
        <label className="block">Name</label>
        <input
          className="w-full rounded border border-gray-700 bg-gray-800 p-1"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
      </div>
      <div>
        <label className="block">Background</label>
        <textarea
          className="w-full rounded border border-gray-700 bg-gray-800 p-1"
          value={background}
          onChange={(e) => setBackground(e.target.value)}
        />
      </div>
      <div>
        <label className="block">Traits</label>
        <textarea
          className="w-full rounded border border-gray-700 bg-gray-800 p-1"
          value={traits}
          onChange={(e) => setTraits(e.target.value)}
        />
      </div>
      <div className="flex gap-2">
        <div>
          <label className="block">HP</label>
          <input
            type="number"
            className="w-20 rounded border border-gray-700 bg-gray-800 p-1"
            value={hp}
            onChange={(e) => setHp(Number(e.target.value))}
          />
        </div>
        <div>
          <label className="block">Strength</label>
          <input
            type="number"
            className="w-20 rounded border border-gray-700 bg-gray-800 p-1"
            value={strength}
            onChange={(e) => setStrength(Number(e.target.value))}
          />
        </div>
        <div>
          <label className="block">Defense</label>
          <input
            type="number"
            className="w-20 rounded border border-gray-700 bg-gray-800 p-1"
            value={defense}
            onChange={(e) => setDefense(Number(e.target.value))}
          />
        </div>
      </div>
      <div>
        <label className="block">Starting Inventory (comma separated)</label>
        <input
          className="w-full rounded border border-gray-700 bg-gray-800 p-1"
          value={inventory}
          onChange={(e) => setInventory(e.target.value)}
        />
      </div>
      <button
        type="submit"
        className="rounded bg-blue-600 px-2 py-1 text-white hover:bg-blue-700"
      >
        Create Character
      </button>
    </form>
  )
}
