import { PageHero } from '@/components/PageHero'
import { SectionHeading } from '@/components/ui/SectionHeading'
import { AnimatedCounter } from '@/components/ui/AnimatedCounter'
import { Reveal, RevealItem } from '@/components/ui/Reveal'
import { stats, news } from '@/data/site'

const timeline = [
  { year: '2007', text: 'Основание компании. Первые жилые объекты на рынке.' },
  { year: '2014', text: 'Старт масштабного микрорайона «Новая Жизнь».' },
  { year: '2019', text: 'Выход на рынки Москвы, МО и Нижнего Новгорода.' },
  { year: '2024', text: 'Более 1,5 млн м² построенной недвижимости.' },
  { year: '2026', text: 'Старт продаж нового квартала «Новая Наганова».' },
]

const geography = [
  'Новая Жизнь, Ульяновск',
  'Новая Наганова, Ульяновск',
  'Шаболовский, Москва',
  'Измайловский парк, Москва',
]

export function About() {
  return (
    <>
      <PageHero
        eyebrow="О компании"
        title={<>Мы создаём <span className="text-gradient">пространства для жизни</span></>}
        description="Наша миссия — качественная недвижимость, которая делает жизнь лучше. Мы не просто строим здания, мы создаём среду, в которой хочется жить."
        crumbs={[{ label: 'О компании' }]}
      />

      {/* Статистика */}
      <section className="container-x">
        <Reveal
          stagger
          className="grid grid-cols-2 gap-px overflow-hidden rounded-3xl border border-line bg-line lg:grid-cols-4"
        >
          {stats.map((s) => (
            <RevealItem key={s.label} className="bg-elev px-6 py-8 text-center">
              <div className="font-display text-4xl md:text-5xl">
                <AnimatedCounter
                  value={s.value}
                  suffix={s.suffix}
                  decimals={s.value % 1 !== 0 ? 1 : 0}
                  className="text-gradient"
                />
              </div>
              <p className="mt-2 text-sm text-muted">{s.label}</p>
            </RevealItem>
          ))}
        </Reveal>
      </section>

      {/* Таймлайн */}
      <section className="container-x py-20 md:py-24">
        <SectionHeading
          eyebrow="История"
          title="Путь длиною в 18 лет"
          subtitle="Каждый год — новые дома, дворы и тысячи семей, которые обрели квартиру мечты."
        />
        <div className="mt-12 grid gap-px overflow-hidden rounded-3xl border border-line bg-line md:grid-cols-5">
          {timeline.map((t, i) => (
            <Reveal
              key={t.year}
              delay={i * 0.08}
              className="relative bg-elev p-6"
            >
              <span className="font-display text-2xl text-brand">{t.year}</span>
              <p className="mt-3 text-sm leading-relaxed text-muted">{t.text}</p>
            </Reveal>
          ))}
        </div>
      </section>

      {/* География + Новости */}
      <section className="container-x grid gap-12 pb-24 lg:grid-cols-2">
        <div>
          <SectionHeading
            eyebrow="География"
            title="Портфель проектов"
            subtitle="Жилые и коммерческие площади в нескольких городах России."
          />
          <Reveal stagger className="mt-8 grid gap-3">
            {geography.map((g) => (
              <RevealItem key={g}>
                <div className="flex items-center gap-3 rounded-2xl border border-line bg-elev px-5 py-4">
                  <span className="size-2 rounded-full bg-brand" />
                  <span className="text-sm font-medium">{g}</span>
                </div>
              </RevealItem>
            ))}
          </Reveal>
        </div>

        <div>
          <SectionHeading eyebrow="Новости" title="Последние события" />
          <Reveal stagger className="mt-8 grid gap-3">
            {news.map((n) => (
              <RevealItem key={n.title}>
                <article className="rounded-2xl border border-line bg-elev p-5 transition-colors hover:border-brand/40">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-brand">{n.tag}</span>
                    <time className="text-faint">{n.date}</time>
                  </div>
                  <p className="mt-2 font-medium">{n.title}</p>
                </article>
              </RevealItem>
            ))}
          </Reveal>
        </div>
      </section>
    </>
  )
}
