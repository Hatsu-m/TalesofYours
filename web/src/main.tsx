import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import './index.css'
import HomePage from './pages/HomePage.tsx'
import PlayPage from './pages/PlayPage.tsx'
import WorldsPage from './pages/WorldsPage.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/play/:gameId" element={<PlayPage />} />
        <Route path="/worlds" element={<WorldsPage />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
