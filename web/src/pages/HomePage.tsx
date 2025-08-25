import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-4 bg-gray-100 p-4 dark:bg-gray-900 dark:text-gray-100">
      <h1 className="text-2xl font-bold">Tales of Yours</h1>
      <Link
        to="/play/demo"
        className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Start Demo
      </Link>
      <Link to="/worlds" className="text-blue-500 underline">
        Browse Worlds
      </Link>
      <Link to="/settings" className="text-blue-500 underline">
        Settings
      </Link>
    </div>
  )
}
