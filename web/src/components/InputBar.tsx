import { useState } from 'react'

interface Props {
  onSend: (text: string) => void
  onCommand: (cmd: string) => void
  disabled?: boolean
}

export default function InputBar({ onSend, onCommand, disabled = false }: Props) {
  const [value, setValue] = useState('')

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = value.trim()
    if (!trimmed) return
    if (trimmed.startsWith('/')) {
      onCommand(trimmed.slice(1))
    } else {
      onSend(trimmed)
    }
    setValue('')
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-gray-700 bg-gray-800 p-4 shadow-inner"
    >
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Type your action... (/save, /party, /help)"
        className="w-full rounded border border-gray-600 bg-gray-800 p-2 shadow-sm placeholder-gray-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-yellow-500"
        disabled={disabled}
        aria-label="Player action"
      />
    </form>
  )
}
