import React from 'react'

export interface Character {
  id: number | string
  name: string
  background?: string
  traits?: string
  stats?: Record<string, number>
  inventory?: string[]
  status?: string
}

interface Props {
  party: Character[]
}

export default function PartyPanel({ party }: Props) {
  if (!party.length) return <div className="text-sm">No party members</div>
  const [player, ...others] = party
  return (
    <div className="space-y-4 text-sm">
      <div>
        <h3 className="font-semibold">Player</h3>
        <div className="mt-1 rounded border border-gray-700 p-2">
          <div className="font-medium">{player.name}</div>
          {player.stats && (
            <div>
              <div>HP: {player.stats.hp ?? 0}</div>
              {player.stats.strength !== undefined && (
                <div>STR: {player.stats.strength}</div>
              )}
              {player.stats.defense !== undefined && (
                <div>DEF: {player.stats.defense}</div>
              )}
            </div>
          )}
          {player.background && <div>Background: {player.background}</div>}
          {player.traits && <div>Traits: {player.traits}</div>}
          {player.inventory && player.inventory.length > 0 && (
            <div>Inventory: {player.inventory.join(', ')}</div>
          )}
          {player.status && <div>Status: {player.status}</div>}
        </div>
      </div>
      {others.length > 0 && (
        <div>
          <h3 className="font-semibold">Party</h3>
          <div className="space-y-2">
            {others.map((m) => (
              <div
                key={m.id}
                className="rounded border border-gray-700 p-2"
              >
                <div className="font-medium">{m.name}</div>
                {m.stats && (
                  <div>
                    <div>HP: {m.stats.hp ?? 0}</div>
                    {m.stats.strength !== undefined && (
                      <div>STR: {m.stats.strength}</div>
                    )}
                    {m.stats.defense !== undefined && (
                      <div>DEF: {m.stats.defense}</div>
                    )}
                  </div>
                )}
                {m.background && <div>Background: {m.background}</div>}
                {m.traits && <div>Traits: {m.traits}</div>}
                {m.inventory && m.inventory.length > 0 && (
                  <div>Inventory: {m.inventory.join(', ')}</div>
                )}
                {m.status && <div>Status: {m.status}</div>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
