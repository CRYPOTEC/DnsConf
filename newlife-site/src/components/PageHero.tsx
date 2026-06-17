import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ChevronRight } from 'lucide-react'
import { EASE } from '@/lib/motion'
import { cn } from '@/lib/cn'

type Crumb = { label: string; to?: string }
type Accent = 'brand' | 'sky' | 'lime' | 'brick'

const accentMap: Record<Accent, { text: string; dot: string; glow: string }> = {
  brand: { text: 'text-brand', dot: 'bg-brand', glow: 'bg-brand/15' },
  sky: { text: 'text-sky', dot: 'bg-sky', glow: 'bg-sky/15' },
  lime: { text: 'text-lime', dot: 'bg-lime', glow: 'bg-lime/15' },
  brick: { text: 'text-brick', dot: 'bg-brick', glow: 'bg-brick/20' },
}

export function PageHero({
  eyebrow,
  title,
  description,
  crumbs = [],
  children,
  accent = 'brand',
}: {
  eyebrow?: string
  title: ReactNode
  description?: string
  crumbs?: Crumb[]
  children?: ReactNode
  accent?: Accent
}) {
  const a = accentMap[accent]
  return (
    <section className="relative overflow-hidden pt-32 pb-12 md:pt-40 md:pb-16">
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-grid opacity-30 mask-fade-b" />
        <div className={cn('absolute left-1/2 top-0 size-[480px] -translate-x-1/2 rounded-full blur-[120px]', a.glow)} />
      </div>

      <div className="container-x">
        <nav className="flex items-center gap-1.5 text-sm text-faint">
          <Link to="/" className="transition-colors hover:text-fg">
            Главная
          </Link>
          {crumbs.map((c) => (
            <span key={c.label} className="flex items-center gap-1.5">
              <ChevronRight className="size-3.5" />
              {c.to ? (
                <Link to={c.to} className="transition-colors hover:text-fg">
                  {c.label}
                </Link>
              ) : (
                <span className="text-muted">{c.label}</span>
              )}
            </span>
          ))}
        </nav>

        {eyebrow && (
          <motion.span
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn(
              'mt-6 inline-flex items-center gap-2 rounded-full border border-line2 bg-elev/60 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em]',
              a.text,
            )}
          >
            <span className={cn('size-1.5 rounded-full', a.dot)} />
            {eyebrow}
          </motion.span>
        )}

        <motion.h1
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: EASE }}
          className="mt-4 max-w-3xl text-4xl sm:text-5xl md:text-6xl"
        >
          {title}
        </motion.h1>

        {description && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.7 }}
            className="mt-5 max-w-2xl text-lg leading-relaxed text-muted"
          >
            {description}
          </motion.p>
        )}

        {children && <div className="mt-8">{children}</div>}
      </div>
    </section>
  )
}
