import { useEffect } from 'react'
import { Route, Routes, useLocation } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { Navbar } from '@/components/Navbar'
import { Footer } from '@/components/Footer'
import { ScrollProgress } from '@/components/ScrollProgress'
import { Home } from '@/pages/Home'
import { ProjectPage } from '@/pages/ProjectPage'
import { Apartments } from '@/pages/Apartments'
import { Mortgage } from '@/pages/Mortgage'
import { About } from '@/pages/About'
import { Contacts } from '@/pages/Contacts'
import { NotFound } from '@/pages/NotFound'
import { projects } from '@/data/site'
import { EASE } from '@/lib/motion'

/** Прокрутка наверх при смене маршрута. */
function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior })
  }, [pathname])
  return null
}

function Page({ children }: { children: React.ReactNode }) {
  return (
    <motion.main
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.35, ease: EASE }}
    >
      {children}
    </motion.main>
  )
}

export default function App() {
  const location = useLocation()
  const newlife = projects.find((p) => p.slug === 'newlife')!
  const naganova = projects.find((p) => p.slug === 'naganova')!

  return (
    <>
      <ScrollProgress />
      <ScrollToTop />
      <Navbar />
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<Page><Home /></Page>} />
          <Route
            path="/newlife"
            element={<Page><ProjectPage project={newlife} /></Page>}
          />
          <Route
            path="/naganova"
            element={<Page><ProjectPage project={naganova} /></Page>}
          />
          <Route path="/apartments" element={<Page><Apartments /></Page>} />
          <Route path="/mortgage" element={<Page><Mortgage /></Page>} />
          <Route path="/about" element={<Page><About /></Page>} />
          <Route path="/contacts" element={<Page><Contacts /></Page>} />
          <Route path="*" element={<Page><NotFound /></Page>} />
        </Routes>
      </AnimatePresence>
      <Footer />
    </>
  )
}
