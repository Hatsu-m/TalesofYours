import { useParams } from 'react-router-dom'
import { useState } from 'react'
import ChatStream, { ChatMessage } from '../components/ChatStream'
import InputBar from '../components/InputBar'

export default function PlayPage() {
  const { gameId } = useParams()
  const [messages, setMessages] = useState<ChatMessage[]>([])

  async function sendAction(text: string) {
    const playerMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'player',
      content: text,
    }
    const dmMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'dm',
      content: '',
    }
    setMessages((prev) => [...prev, playerMsg, dmMsg])

    try {
      const resp = await fetch(`/games/${gameId}/turn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })
      const reader = resp.body?.getReader()
      const decoder = new TextDecoder()
      if (!reader) return
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        setMessages((prev) =>
          prev.map((m) =>
            m.id === dmMsg.id
              ? { ...m, content: m.content + decoder.decode(value) }
              : m,
          ),
        )
      }
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === dmMsg.id ? { ...m, content: '[error streaming]' } : m,
        ),
      )
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
    <div className="flex h-full flex-col md:flex-row dark:bg-gray-900 dark:text-gray-100">
      <aside className="hidden w-64 border-r border-gray-700 p-4 md:block">Left Panel</aside>
      <main className="flex flex-1 flex-col">
        <ChatStream messages={messages} />
        <InputBar onSend={sendAction} onCommand={handleCommand} />
      </main>
      <aside className="hidden w-64 border-l border-gray-700 p-4 md:block">Right Panel</aside>
    </div>
  )
}
