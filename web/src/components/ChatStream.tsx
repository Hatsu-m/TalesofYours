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
    <Virtuoso
      data={messages}
      followOutput="smooth"
      className="flex-1 overflow-y-auto p-4"
      itemContent={(_, msg) => (
        <div
          className={`mb-2 whitespace-pre-wrap ${
            msg.role === 'player' ? 'text-blue-300' : 'text-gray-100'
          }`}
        >
          {msg.content}
        </div>
      )}
    />
  )
}
