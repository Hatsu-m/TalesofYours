import { useParams } from 'react-router-dom'

export default function PlayPage() {
  const { gameId } = useParams()
  return (
    <div className="flex h-full flex-col md:flex-row dark:bg-gray-900 dark:text-gray-100">
      <aside className="hidden w-64 border-r border-gray-700 p-4 md:block">Left Panel</aside>
      <main className="flex flex-1 flex-col">
        <div className="flex-1 overflow-y-auto p-4">Story for game {gameId}</div>
        <div className="border-t border-gray-700 p-4">
          <input
            type="text"
            placeholder="Type your action..."
            className="w-full rounded border border-gray-700 bg-gray-800 p-2"
          />
        </div>
      </main>
      <aside className="hidden w-64 border-l border-gray-700 p-4 md:block">Right Panel</aside>
    </div>
  )
}
