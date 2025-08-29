import { Link, useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import ChatStream, { type ChatMessage } from '../components/ChatStream'
import InputBar from '../components/InputBar'
import RollPrompt, { type RollRequest } from '../components/RollPrompt'
import RulesBadge from '../components/RulesBadge'
import PartyPanel, { type Character } from '../components/PartyPanel'
import CreateCharacterForm, {
  type NewCharacter,
} from '../components/CreateCharacterForm'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function PlayPage() {
  const { gameId } = useParams()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [pendingRoll, setPendingRoll] = useState<RollRequest | null>(null)
  const [rulesInfo, setRulesInfo] = useState<{
    label: string
    instructions: string
  } | null>(null)
  const [worldTitle, setWorldTitle] = useState<string | null>(null)
  const [party, setParty] = useState<Character[]>([])
  const [showCreator, setShowCreator] = useState(false)
  const [statKeys, setStatKeys] = useState<string[]>([])
  const [model] = useState<string>(
    () => localStorage.getItem('model') ?? 'llama3',
  )

  useEffect(() => {
    if (gameId) {
      localStorage.setItem('gameId', gameId)
    }
  }, [gameId])

  useEffect(() => {
      async function loadRules() {
        const game = await fetch(`${API_BASE}/games/${gameId}`).then((r) => r.json())
        const world = await fetch(`${API_BASE}/worlds/${game.world_id}`).then((r) =>
          r.json(),
        )
        setParty(game.party ?? [])
        setStatKeys(world.stats ?? [])
      const map: Record<string, { label: string; instructions: string }> = {
        dnd5e: {
          label: 'D&D 5e',
          instructions:
            'Use Dungeons & Dragons 5th Edition rules. A 20 always succeeds and a 1 always fails.',
        },
        custom_d6: {
          label: 'Custom d6',
          instructions:
            'Roll a single d6 for checks. A 6 always succeeds and a 1 always fails.',
        },
      }
      setRulesInfo(map[world.ruleset])
      setWorldTitle(world.title)
    }
    loadRules()
  }, [gameId])

  async function sendAction(text: string) {
    const playerMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'player',
      content: text,
    }
    setMessages((prev) => [...prev, playerMsg])

    try {
      const resp = await fetch(`${API_BASE}/games/${gameId}/turn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, model }),
      })
      if (!resp.ok) throw new Error('request failed')
      const data = await resp.json()
      const dmMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'dm',
        content: data.message,
      }
      setMessages((prev) => [...prev, dmMsg])
      if (data.awaiting_player_roll && data.roll_request) {
        setPendingRoll(data.roll_request as RollRequest)
      } else {
        setPendingRoll(null)
      }
    } catch {
      const errMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'dm',
        content: '[error fetching turn]',
      }
      setMessages((prev) => [...prev, errMsg])
    }
  }

  async function submitRoll(value: number, mod: number) {
    if (!pendingRoll) return
    const playerMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'player',
      content: `Roll ${value}${mod ? ` + ${mod}` : ''}`,
    }
    setMessages((prev) => [...prev, playerMsg])
    const resp = await fetch(`${API_BASE}/games/${gameId}/player-roll`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        request_id: pendingRoll.id,
        value,
        mod,
      }),
    })
    if (!resp.ok) {
      throw new Error('invalid roll')
    }
    const data = await resp.json()
    const dmMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'dm',
      content: data.message,
    }
    setMessages((prev) => [...prev, dmMsg])
    if (data.awaiting_player_roll && data.roll_request) {
      setPendingRoll(data.roll_request as RollRequest)
    } else {
      setPendingRoll(null)
    }
  }

  async function saveGame() {
    if (!gameId) return
    await fetch(`${API_BASE}/games/${gameId}/save`, { method: 'POST' })
  }

  async function exportGame() {
    if (!gameId) return
    const resp = await fetch(`${API_BASE}/games/${gameId}/export`)
    if (!resp.ok) return
    const data = await resp.json()
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `game-${gameId}-save.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  function handleCommand(cmd: string) {
    switch (cmd) {
      case 'save':
        void saveGame()
        break
      case 'party':
        console.log('show party')
        break
      case 'help':
        console.log('show help')
        break
      default:
        console.log('unknown command', cmd)
    }
  }

  return (
    <div className="relative flex h-full flex-col md:flex-row dark:bg-gray-900 dark:text-gray-100">
      <Link
        to="/"
        className="absolute left-2 top-2 rounded bg-blue-600 px-2 py-1 text-white hover:bg-blue-700"
      >
        Home
      </Link>
      <Link
        to="/settings"
        className="absolute right-2 top-2 rounded bg-gray-700 px-2 py-1 text-white hover:bg-gray-800"
      >
        Settings
      </Link>
      {rulesInfo && (
        <RulesBadge
          name={rulesInfo.label}
          description={rulesInfo.instructions}
        />
      )}
      <aside className="hidden w-64 border-r border-gray-700 p-4 pt-10 md:block">
        {worldTitle && (
          <div className="text-sm font-semibold">Story: {worldTitle}</div>
        )}
        <div className="mt-4 flex flex-col space-y-2">
          <button
            onClick={saveGame}
            className="rounded bg-blue-600 px-2 py-1 text-white hover:bg-blue-700"
          >
            Save
          </button>
          <button
            onClick={exportGame}
            className="rounded bg-gray-700 px-2 py-1 text-white hover:bg-gray-800"
          >
            Export
          </button>
        </div>
      </aside>
      <main className="flex flex-1 flex-col">
        <ChatStream messages={messages} />
        {pendingRoll && (
          <RollPrompt request={pendingRoll} onSubmit={submitRoll} />
        )}
        <InputBar
          onSend={sendAction}
          onCommand={handleCommand}
          disabled={!!pendingRoll}
        />
      </main>
      <aside className="hidden w-64 border-l border-gray-700 p-4 pt-10 md:block">
        {party.length === 0 ? (
          showCreator ? (
            <CreateCharacterForm
              gameId={gameId!}
              statKeys={statKeys}
              onCreated={(c: NewCharacter) => {
                setParty([c])
                setShowCreator(false)
              }}
            />
          ) : (
            <button
              onClick={() => setShowCreator(true)}
              className="rounded bg-blue-600 px-2 py-1 text-white hover:bg-blue-700"
            >
              Create Character
            </button>
          )
        ) : (
          <PartyPanel party={party} />
        )}
      </aside>
    </div>
  )
}
