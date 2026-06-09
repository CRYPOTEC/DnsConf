import { Check, MapPin } from 'lucide-react'
import { PageHero } from '@/components/PageHero'
import { SectionHeading } from '@/components/ui/SectionHeading'
import { Reveal, RevealItem } from '@/components/ui/Reveal'
import { ButtonLink } from '@/components/ui/Button'
import { LeadForm } from '@/components/LeadForm'
import { type Project, type ProjectShot } from '@/data/site'
import { asset } from '@/lib/asset'
import { cn } from '@/lib/cn'

const accentCls: Record<Project['accent'], { text: string; soft: string; ring: string; glow: string }> = {
  brand: { text: 'text-brand', soft: 'bg-brand/10', ring: 'hover:border-brand/50', glow: 'var(--color-brand)' },
  sky: { text: 'text-sky', soft: 'bg-sky/10', ring: 'hover:border-sky/50', glow: 'var(--color-sky)' },
  lime: { text: 'text-lime', soft: 'bg-lime/10', ring: 'hover:border-lime/50', glow: 'var(--color-lime)' },
}

// Цвет ярлыка по типу кадра: дома — терракота, двор/озеленение — зелёный,
// микрорайон/рендер/генплан — синий, интерьеры — глина.
const tagColor: Record<string, string> = {
  'Дома': 'text-brand',
  'Двор': 'text-lime',
  'Благоустройство': 'text-lime',
  'Озеленение': 'text-lime',
  'Микрорайон': 'text-sky',
  'Рендер': 'text-sky',
  'Генплан': 'text-sky',
  'Внутри': 'text-clay',
}

export function ProjectPage({ project }: { project: Project }) {
  const a = accentCls[project.accent]

  return (
    <>
      <PageHero
        eyebrow={`${project.kind} · ${project.status}`}
        title={project.name}
        description={project.description}
        crumbs={[{ label: project.name }]}
      >
        <div className="flex flex-wrap items-center gap-4">
          <ButtonLink to="/apartments">Выбрать квартиру</ButtonLink>
          <ButtonLink to="/mortgage" variant="outline">
            Рассчитать ипотеку
          </ButtonLink>
          <span className="flex items-center gap-2 text-sm text-muted">
            <MapPin className={cn('size-4', a.text)} /> Ульяновск
          </span>
        </div>
      </PageHero>

      {/* Большое фото проекта */}
      <section className="container-x">
        <Reveal>
          <div className="relative overflow-hidden rounded-[2rem] border border-line">
            <img
              src={asset(project.hero)}
              alt={project.name}
              className="aspect-[16/10] w-full object-cover object-center sm:aspect-[21/9]"
            />
            <div
              className="pointer-events-none absolute inset-0"
              style={{ background: `linear-gradient(to top, color-mix(in srgb, ${a.glow} 30%, transparent), transparent 55%)` }}
            />
          </div>
        </Reveal>
      </section>

      {/* Бейджи проекта */}
      <section className="container-x mt-6">
        <Reveal
          stagger
          className="grid grid-cols-3 gap-px overflow-hidden rounded-3xl border border-line bg-line"
        >
          {project.badges.map((b) => (
            <RevealItem key={b.label} className="bg-elev px-6 py-7 text-center">
              <p className="text-xs uppercase tracking-wide text-faint">
                {b.label}
              </p>
              <p className={cn('mt-1 font-display text-2xl md:text-3xl', a.text)}>
                {b.value}
              </p>
            </RevealItem>
          ))}
        </Reveal>
      </section>

      {/* Преимущества проекта */}
      <section className="container-x py-20 md:py-24">
        <SectionHeading
          eyebrow="Концепция"
          title={project.tagline}
          subtitle="Всё, что делает жизнь в проекте комфортной каждый день."
        />
        <Reveal stagger className="mt-10 grid gap-4 sm:grid-cols-2">
          {project.highlights.map((h) => (
            <RevealItem key={h}>
              <div className="flex items-start gap-4 rounded-2xl border border-line bg-elev p-6">
                <span className={cn('grid size-10 shrink-0 place-items-center rounded-xl', a.soft, a.text)}>
                  <Check className="size-5" />
                </span>
                <p className="text-base text-fg/90">{h}</p>
              </div>
            </RevealItem>
          ))}
        </Reveal>
      </section>

      {/* Галерея проекта — дома, дворы, благоустройство */}
      <section className="container-x pb-20 md:pb-24">
        <SectionHeading
          eyebrow="Галерея"
          title="Дома, дворы и благоустройство"
          subtitle="Реальные фотографии и архитектурные виды проекта."
        />
        <Reveal stagger className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {project.shots.map((s) => (
            <RevealItem key={s.src + s.title}>
              <ShotTile shot={s} />
            </RevealItem>
          ))}
        </Reveal>
      </section>

      {/* Заявка */}
      <section className="container-x pb-24">
        <div className="rounded-[2rem] border border-line bg-elev p-8 md:p-10">
          <div className="grid items-center gap-8 lg:grid-cols-2">
            <div>
              <h2 className="text-3xl md:text-4xl">
                Узнать цены и планировки {project.name}
              </h2>
              <p className="mt-4 max-w-md text-muted">
                Оставьте заявку — пришлём актуальный прайс, свободные квартиры и
                условия покупки.
              </p>
            </div>
            <div className="rounded-2xl border border-line bg-base/60 p-6">
              <LeadForm />
            </div>
          </div>
        </div>
      </section>
    </>
  )
}

function ShotTile({ shot }: { shot: ProjectShot }) {
  return (
    <div className="group relative aspect-[4/3] overflow-hidden rounded-2xl border border-line bg-elev">
      <img
        src={asset(shot.src)}
        alt={shot.title}
        loading="lazy"
        className="size-full object-cover transition-transform duration-500 group-hover:scale-[1.06]"
      />
      <span
        className={cn(
          'absolute left-3 top-3 rounded-full bg-base/90 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide backdrop-blur',
          tagColor[shot.tag] ?? 'text-brand',
        )}
      >
        {shot.tag}
      </span>
      <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-ink/85 to-transparent p-4 pt-10">
        <p className="text-sm font-semibold text-[#fdf6ec]">{shot.title}</p>
      </div>
    </div>
  )
}
