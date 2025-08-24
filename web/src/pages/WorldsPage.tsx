import { Link } from 'react-router-dom'

export default function WorldsPage() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-4 bg-gray-100 p-4 dark:bg-gray-900 dark:text-gray-100">
      <h1 className="text-2xl font-bold">Worlds</h1>
      <Link to="/" className="text-blue-500 underline">
        Back
      </Link>
    </div>
  )
}
