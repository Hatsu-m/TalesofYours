import { useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import ChatStream, { type ChatMessage } from '../components/ChatStream'
import InputBar from '../components/InputBar'
import RollPrompt, { type RollRequest } from '../components/RollPrompt'
import RulesBadge from '../components/RulesBadge'

export default function PlayPage() {
  const { gameId } = useParams()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [pendingRoll, setPendingRoll] = useState<RollRequest | null>(null)
  const [rulesInfo, setRulesInfo] = useState<
    { label: string; instructions: string } | null
  >(null)

  useEffect(() => {
    async function loadRules() {
      const game = await fetch(`/games/${gameId}`).then((r) => r.json())
      const world = await fetch(`/worlds/${game.world_id}`).then((r) => r.json())
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
      const resp = await fetch(`/games/${gameId}/turn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
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
    const resp = await fetch(`/games/${gameId}/player-roll`, {
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

  function handleCommand(cmd: string) {
    switch (cmd) {
      case 'save':
        console.log('save game')
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
      {rulesInfo && (
        <RulesBadge
          name={rulesInfo.label}
          description={rulesInfo.instructions}
        />
      )}
      <aside className="hidden w-64 border-r border-gray-700 p-4 md:block">Left Panel</aside>
      <main className="flex flex-1 flex-col">
        <ChatStream messages={messages} />
        {pendingRoll && <RollPrompt request={pendingRoll} onSubmit={submitRoll} />}
        <InputBar
          onSend={sendAction}
          onCommand={handleCommand}
          disabled={!!pendingRoll}
        />
      </main>
      <aside className="hidden w-64 border-l border-gray-700 p-4 md:block">Right Panel</aside>
    </div>
  )
}
