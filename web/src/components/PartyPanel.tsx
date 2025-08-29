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
        <CharacterCard member={player} />
      </div>
      {others.length > 0 && (
        <div>
          <h3 className="font-semibold">Party</h3>
          <div className="space-y-2">
            {others.map((m) => (
              <CharacterCard key={m.id} member={m} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function CharacterCard({ member }: { member: Character }) {
  return (
    <details className="rounded border border-gray-700 p-2">
      <summary className="flex cursor-pointer justify-between">
        <span className="font-medium">{member.name}</span>
        {member.stats && (
          <span>
            HP: {member.stats.hp ?? 0}
            {member.stats.strength !== undefined && (
              <span className="ml-2">STR: {member.stats.strength}</span>
            )}
            {member.stats.defense !== undefined && (
              <span className="ml-2">DEF: {member.stats.defense}</span>
            )}
          </span>
        )}
      </summary>
      <div className="mt-2 space-y-1">
        {member.background && <div>Background: {member.background}</div>}
        {member.traits && <div>Traits: {member.traits}</div>}
        {member.inventory && member.inventory.length > 0 && (
          <div>Inventory: {member.inventory.join(', ')}</div>
        )}
        {member.status && <div>Status: {member.status}</div>}
      </div>
    </details>
  )
}
