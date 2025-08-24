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
    <form onSubmit={handleSubmit} className="border-t border-gray-700 p-4">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Type your action... (/save, /party, /help)"
        className="w-full rounded border border-gray-700 bg-gray-800 p-2"
        disabled={disabled}
      />
    </form>
  )
}
