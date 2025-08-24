import { useState } from 'react'

interface Props {
  name: string
  description: string
}

export default function RulesBadge({ name, description }: Props) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="absolute right-2 top-2 rounded bg-gray-700 px-2 py-1 text-xs"
      >
        {name}
      </button>
      {open && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/50">
          <div className="max-w-sm rounded bg-white p-4 text-sm dark:bg-gray-800 dark:text-gray-100">
            <h2 className="mb-2 text-lg font-bold">{name} Rules</h2>
            <p className="whitespace-pre-wrap">{description}</p>
            <button
              onClick={() => setOpen(false)}
              className="mt-4 rounded bg-blue-600 px-3 py-1 text-white"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </>
  )
}
