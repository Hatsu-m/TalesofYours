import { Virtuoso } from 'react-virtuoso'

export type ChatMessage = {
  id: string
  role: 'player' | 'dm'
  content: string
}

interface Props {
  messages: ChatMessage[]
}

export default function ChatStream({ messages }: Props) {
  return (
    <div role="log" aria-live="polite" className="flex-1 overflow-y-auto">
      <Virtuoso
        data={messages}
        followOutput="smooth"
        className="p-4"
        itemContent={(_, msg) => (
          <div
            className={`mb-2 whitespace-pre-wrap ${
              msg.role === 'player' ? 'text-blue-200' : 'text-gray-100'
            }`}
          >
            <span className="font-semibold">
              {msg.role === 'player' ? 'Player' : 'DM'}:
            </span>{' '}
            {msg.content}
          </div>
        )}
      />
    </div>
  )
}
