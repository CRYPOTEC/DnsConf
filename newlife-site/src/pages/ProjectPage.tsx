import { Check, MapPin } from 'lucide-react'
import { PageHero } from '@/components/PageHero'
import { SectionHeading } from '@/components/ui/SectionHeading'
import { Reveal, RevealItem } from '@/components/ui/Reveal'
import { ButtonLink } from '@/components/ui/Button'
import { LeadForm } from '@/components/LeadForm'
import { galleryItems, type Project } from '@/data/site'

export function ProjectPage({ project }: { project: Project }) {
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
            <MapPin className="size-4 text-brand" /> Ульяновск
          </span>
        </div>
      </PageHero>

      {/* Бейджи проекта */}
      <section className="container-x">
        <Reveal
          stagger
          className="grid grid-cols-3 gap-px overflow-hidden rounded-3xl border border-line bg-line"
        >
          {project.badges.map((b) => (
            <RevealItem key={b.label} className="bg-elev px-6 py-7 text-center">
              <p className="text-xs uppercase tracking-wide text-faint">
                {b.label}
              </p>
              <p className="mt-1 font-display text-2xl text-brand md:text-3xl">
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
                <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-brand/10 text-brand">
                  <Check className="size-5" />
                </span>
                <p className="text-base text-fg/90">{h}</p>
              </div>
            </RevealItem>
          ))}
        </Reveal>
      </section>

      {/* Галерея */}
      <section className="container-x pb-20 md:pb-24">
        <SectionHeading eyebrow="Галерея" title="Как это выглядит" />
        <Reveal stagger className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {galleryItems.map((g) => (
            <RevealItem key={g.title}>
              <GalleryTile title={g.title} hue={g.hue} />
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

function GalleryTile({ title, hue }: { title: string; hue: number }) {
  return (
    <div className="group relative aspect-[4/3] overflow-hidden rounded-2xl border border-line">
      <div
        className="absolute inset-0 transition-transform duration-500 group-hover:scale-105"
        style={{
          background: `linear-gradient(135deg, hsl(${hue} 45% 16%), hsl(${hue + 20} 55% 9%))`,
        }}
      />
      {/* стилизованные «здания» */}
      <svg viewBox="0 0 200 150" className="absolute inset-0 size-full opacity-40">
        {[20, 60, 100, 140].map((x, i) => (
          <rect
            key={x}
            x={x}
            y={60 + (i % 2) * 20}
            width="34"
            height={90 - (i % 2) * 20}
            rx="3"
            fill="none"
            stroke={`hsl(${hue} 70% 60%)`}
            strokeOpacity="0.5"
          />
        ))}
      </svg>
      <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-ink/90 to-transparent p-5">
        <p className="font-display text-lg">{title}</p>
      </div>
    </div>
  )
}
