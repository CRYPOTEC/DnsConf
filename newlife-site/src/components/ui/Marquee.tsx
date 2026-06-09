import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

type Props = {
  items: ReactNode[]
  duration?: number
  className?: string
}

/** Бесконечная бегущая строка (дублирует контент для бесшовности). */
export function Marquee({ items, duration = 32, className }: Props) {
  return (
    <div className={cn('mask-fade-x overflow-hidden', className)}>
      <div
        className="flex w-max animate-marquee gap-4"
        style={{ '--marquee-duration': `${duration}s` } as React.CSSProperties}
      >
        {[...items, ...items].map((item, i) => (
          <div key={i} className="shrink-0">
            {item}
          </div>
        ))}
      </div>
    </div>
  )
}
