import { Reveal } from './Reveal'
import { cn } from '@/lib/cn'

type Props = {
  eyebrow?: string
  title: string
  subtitle?: string
  align?: 'left' | 'center'
  className?: string
}

/** Единый заголовок секции: надзаголовок + крупный тайтл + подпись. */
export function SectionHeading({
  eyebrow,
  title,
  subtitle,
  align = 'left',
  className,
}: Props) {
  return (
    <Reveal
      className={cn(
        'max-w-2xl',
        align === 'center' && 'mx-auto text-center',
        className,
      )}
    >
      {eyebrow && (
        <span className="mb-4 inline-flex items-center gap-2 rounded-full border border-line2 bg-elev/50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-brand">
          <span className="size-1.5 rounded-full bg-brand" />
          {eyebrow}
        </span>
      )}
      <h2 className="text-balance text-3xl sm:text-4xl md:text-5xl">{title}</h2>
      {subtitle && (
        <p className="mt-4 text-base leading-relaxed text-muted sm:text-lg">
          {subtitle}
        </p>
      )}
    </Reveal>
  )
}
