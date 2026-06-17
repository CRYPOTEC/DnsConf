import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, HashRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'

// На GitHub Pages (подпапка, без серверного фолбэка) используем HashRouter,
// чтобы прямые ссылки и обновление страницы не давали 404. В обычной сборке —
// чистые URL через BrowserRouter.
const Router = import.meta.env.VITE_HASH_ROUTER === '1' ? HashRouter : BrowserRouter

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Router>
      <App />
    </Router>
  </StrictMode>,
)
