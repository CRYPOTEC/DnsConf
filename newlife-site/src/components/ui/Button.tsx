import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { cn } from '@/lib/cn'
import { Magnetic } from './Magnetic'

type Variant = 'primary' | 'ghost' | 'outline'

const base =
  'group relative inline-flex items-center justify-center gap-2 rounded-full px-6 py-3 text-sm font-semibold tracking-tight transition-colors duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand/60'

const styles: Record<Variant, string> = {
  primary:
    'bg-brand text-ink shadow-[0_10px_40px_-12px_var(--color-brand)] hover:bg-brand-2',
  outline:
    'border border-line2 text-fg hover:border-brand hover:text-brand bg-elev/40',
  ghost: 'text-fg hover:text-brand',
}

type CommonProps = {
  children: ReactNode
  variant?: Variant
  className?: string
  magnetic?: boolean
}

function Inner({ children }: { children: ReactNode }) {
  return <span className="inline-flex items-center gap-2">{children}</span>
}

export function ButtonLink({
  to,
  external,
  children,
  variant = 'primary',
  className,
  magnetic = true,
}: CommonProps & { to: string; external?: boolean }) {
  const cls = cn(base, styles[variant], className)
  const content = <Inner>{children}</Inner>

  const node = external ? (
    <a href={to} className={cls} target="_blank" rel="noreferrer">
      {content}
    </a>
  ) : (
    <Link to={to} className={cls}>
      {content}
    </Link>
  )

  return magnetic ? <Magnetic>{node}</Magnetic> : node
}

export function Button({
  children,
  variant = 'primary',
  className,
  onClick,
  type = 'button',
}: CommonProps & {
  onClick?: () => void
  type?: 'button' | 'submit'
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      className={cn(base, styles[variant], className)}
    >
      <Inner>{children}</Inner>
    </button>
  )
}
