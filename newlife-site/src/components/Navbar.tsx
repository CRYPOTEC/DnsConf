import { useEffect, useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { Menu, Phone, X } from 'lucide-react'
import { company, nav } from '@/data/site'
import { ButtonLink } from './ui/Button'
import { cn } from '@/lib/cn'

export function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 16)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    document.body.style.overflow = open ? 'hidden' : ''
  }, [open])

  return (
    <header className="fixed inset-x-0 top-0 z-50">
      <div className="container-x">
        <div
          className={cn(
            'mt-3 flex items-center justify-between rounded-2xl px-4 py-2.5 transition-all duration-500',
            scrolled
              ? 'glass shadow-[0_12px_44px_-20px_rgba(46,32,20,0.35)]'
              : 'border border-transparent',
          )}
        >
          <Link to="/" className="flex items-center gap-2.5" aria-label="Новая">
            <Logo />
            <span className="font-display text-lg font-bold tracking-tight">
              {company.name}
            </span>
          </Link>

          <nav className="hidden items-center gap-1 lg:flex">
            {nav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    'rounded-full px-3.5 py-2 text-sm font-medium transition-colors duration-200',
                    isActive
                      ? 'text-brand'
                      : 'text-muted hover:text-fg',
                  )
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="hidden items-center gap-3 lg:flex">
            <a
              href={company.phoneHref}
              className="flex items-center gap-2 text-sm font-semibold text-fg transition-colors hover:text-brand"
            >
              <Phone className="size-4" />
              {company.phone}
            </a>
            <ButtonLink to="/contacts" className="px-5 py-2.5">
              Оставить заявку
            </ButtonLink>
          </div>

          <button
            className="grid size-10 place-items-center rounded-xl border border-line2 text-fg lg:hidden"
            onClick={() => setOpen(true)}
            aria-label="Меню"
          >
            <Menu className="size-5" />
          </button>
        </div>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-ink/80 backdrop-blur-md lg:hidden"
          >
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', stiffness: 260, damping: 30 }}
              className="absolute right-0 top-0 flex h-full w-[82%] max-w-sm flex-col gap-2 border-l border-line bg-base p-6"
            >
              <div className="mb-6 flex items-center justify-between">
                <span className="font-display text-lg font-bold">Меню</span>
                <button
                  onClick={() => setOpen(false)}
                  className="grid size-10 place-items-center rounded-xl border border-line2"
                  aria-label="Закрыть"
                >
                  <X className="size-5" />
                </button>
              </div>
              {nav.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={() => setOpen(false)}
                  className={({ isActive }) =>
                    cn(
                      'rounded-xl px-4 py-3 text-lg font-semibold transition-colors',
                      isActive
                        ? 'bg-elev text-brand'
                        : 'text-fg hover:bg-elev',
                    )
                  }
                >
                  {item.label}
                </NavLink>
              ))}
              <div className="mt-auto flex flex-col gap-3">
                <a
                  href={company.phoneHref}
                  className="flex items-center gap-2 text-base font-semibold"
                >
                  <Phone className="size-4 text-brand" />
                  {company.phone}
                </a>
                <ButtonLink
                  to="/contacts"
                  magnetic={false}
                  className="w-full"
                >
                  Оставить заявку
                </ButtonLink>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}

export function Logo({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        'grid size-9 place-items-center rounded-xl bg-gradient-to-br from-brand to-brand-2 text-on-brand shadow-[0_8px_24px_-10px_var(--color-brand)]',
        className,
      )}
    >
      <svg viewBox="0 0 24 24" className="size-5" fill="none">
        <path
          d="M4 20V8.5L12 3l8 5.5V20h-5v-6H9v6H4Z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinejoin="round"
        />
      </svg>
    </span>
  )
}
