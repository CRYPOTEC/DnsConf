import { Link } from 'react-router-dom'
import { ArrowUpRight, Check } from 'lucide-react'
import { TiltCard } from './ui/TiltCard'
import type { Project } from '@/data/site'
import { cn } from '@/lib/cn'
import { asset } from '@/lib/asset'

const accentMap = {
  brand: { text: 'text-brand', ring: 'group-hover:border-brand/50', glow: 'var(--color-brand)' },
  sky: { text: 'text-sky', ring: 'group-hover:border-sky/50', glow: 'var(--color-sky)' },
  lime: { text: 'text-lime', ring: 'group-hover:border-lime/50', glow: 'var(--color-lime)' },
  brick: { text: 'text-brick', ring: 'group-hover:border-brick/50', glow: 'var(--color-brick)' },
}

export function ProjectCard({ project }: { project: Project }) {
  const a = accentMap[project.accent]
  return (
    <TiltCard className="group h-full">
      <Link
        to={project.to}
        className={cn(
          'relative flex h-full flex-col overflow-hidden rounded-3xl border border-line bg-elev p-7 transition-colors duration-300',
          a.ring,
        )}
      >
        {/* Реальный фасад проекта */}
        <ProjectPhoto src={asset(project.image)} alt={project.name} glow={a.glow} />

        <div className="relative flex items-center justify-between">
          <span className="rounded-full border border-line2 bg-base/60 px-3 py-1 text-xs font-semibold text-muted">
            {project.kind}
          </span>
          <span className={cn('text-xs font-semibold uppercase tracking-wide', a.text)}>
            {project.status}
          </span>
        </div>

        <h3 className="relative mt-28 text-3xl md:text-4xl">{project.name}</h3>
        <p className={cn('relative mt-1 text-sm font-semibold', a.text)}>
          {project.tagline}
        </p>
        <p className="relative mt-4 text-sm leading-relaxed text-muted">
          {project.description}
        </p>

        <ul className="relative mt-6 grid gap-2">
          {project.highlights.slice(0, 3).map((h) => (
            <li key={h} className="flex items-start gap-2 text-sm text-fg/90">
              <Check className={cn('mt-0.5 size-4 shrink-0', a.text)} />
              {h}
            </li>
          ))}
        </ul>

        <div className="relative mt-7 flex items-center justify-between border-t border-line pt-5">
          <div className="flex gap-4">
            {project.badges.map((b) => (
              <div key={b.label}>
                <p className="text-[11px] uppercase tracking-wide text-faint">
                  {b.label}
                </p>
                <p className="text-sm font-bold text-fg">{b.value}</p>
              </div>
            ))}
          </div>
          <span className={cn('grid size-11 place-items-center rounded-full border border-line2 transition-colors', a.text, a.ring)}>
            <ArrowUpRight className="size-5 transition-transform duration-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
          </span>
        </div>
      </Link>
    </TiltCard>
  )
}

function ProjectPhoto({
  src,
  alt,
  glow,
}: {
  src: string
  alt: string
  glow: string
}) {
  return (
    <div className="pointer-events-none absolute inset-x-0 top-0 h-48 overflow-hidden rounded-t-3xl">
      <img
        src={src}
        alt={alt}
        className="size-full object-cover transition-transform duration-700 ease-[cubic-bezier(0.22,1,0.36,1)] group-hover:scale-105"
        loading="lazy"
      />
      {/* затемнение сверху для читаемости чипов */}
      <div className="absolute inset-x-0 top-0 h-20 bg-gradient-to-b from-black/25 to-transparent" />
      {/* мягкое растворение фото в карточке снизу */}
      <div className="absolute inset-0 bg-gradient-to-t from-elev via-elev/35 to-transparent" />
      {/* акцентное свечение проекта */}
      <div
        className="absolute -right-10 -top-16 size-52 rounded-full blur-3xl"
        style={{
          background: `radial-gradient(circle, color-mix(in srgb, ${glow} 35%, transparent), transparent 70%)`,
        }}
      />
    </div>
  )
}
