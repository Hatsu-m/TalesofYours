import { useState } from 'react'

export interface RollRequest {
  id: string
  skill: string
  sides: number
  dc?: number | null
}

interface Props {
  request: RollRequest
  onSubmit: (value: number, mod: number) => Promise<void> | void
}

export default function RollPrompt({ request, onSubmit }: Props) {
  const [value, setValue] = useState('')
  const [mod, setMod] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [rolling, setRolling] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const rollValue = parseInt(value, 10)
    if (isNaN(rollValue) || rollValue < 1 || rollValue > request.sides) {
      setError(`Enter a number between 1 and ${request.sides}`)
      return
    }
    try {
      setRolling(true)
      await onSubmit(rollValue, mod)
      setTimeout(() => setRolling(false), 600)
      setValue('')
      setMod(0)
      setError(null)
    } catch (err) {
      setRolling(false)
      setError((err as Error).message)
    }
  }

  return (
    <div className="border-b border-yellow-600 bg-yellow-800 p-4 text-yellow-100 shadow">
      <div className="mb-2 flex items-center font-semibold">
        <span
          className={`mr-2 inline-block ${rolling ? 'animate-roll' : ''}`}
          aria-hidden="true"
        >
          🎲
        </span>
        Roll a d{request.sides} for {request.skill}
        {request.dc !== undefined && request.dc !== null && ` (DC ${request.dc})`}
      </div>
      <form onSubmit={handleSubmit} className="flex items-center gap-2">
        <input
          type="number"
          min={1}
          max={request.sides}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          className="w-20 rounded p-1 text-gray-900 shadow-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-yellow-400"
        />
        <span>+</span>
        <input
          type="number"
          value={mod}
          onChange={(e) => setMod(Number(e.target.value))}
          className="w-16 rounded p-1 text-gray-900 shadow-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-yellow-400"
        />
        <button
          type="submit"
          className="rounded bg-yellow-600 px-3 py-1 text-gray-900 shadow focus:outline-none focus-visible:ring-2 focus-visible:ring-yellow-400"
        >
          Submit
        </button>
      </form>
      {error && <div className="mt-2 text-red-200">{error}</div>}
    </div>
  )
}

