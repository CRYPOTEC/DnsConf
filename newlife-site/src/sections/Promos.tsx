import { Link } from 'react-router-dom'
import { ArrowUpRight } from 'lucide-react'
import { SectionHeading } from '@/components/ui/SectionHeading'
import { Marquee } from '@/components/ui/Marquee'
import { Reveal, RevealItem } from '@/components/ui/Reveal'
import { promos } from '@/data/site'
import { cn } from '@/lib/cn'

// Разные цвета акций для разнообразия палитры.
const promoColors = [
  { tag: 'bg-sky/12 text-sky', link: 'text-sky', border: 'hover:border-sky/50' },
  { tag: 'bg-lime/15 text-lime', link: 'text-lime', border: 'hover:border-lime/50' },
  { tag: 'bg-brand/10 text-brand', link: 'text-brand', border: 'hover:border-brand/50' },
  { tag: 'bg-clay/12 text-clay', link: 'text-clay', border: 'hover:border-clay/50' },
]

const ticker = [
  'Семейная ипотека от 6%',
  'Скидки до 15%',
  'Trade-in',
  'Отделка под ключ',
  'Старт продаж «Новая Наганова»',
  'Рассрочка от застройщика',
]

export function Promos() {
  return (
    <section className="py-24 md:py-28">
      <div className="container-x">
        <SectionHeading
          eyebrow="Выгодные предложения"
          title="Купить квартиру выгоднее, чем кажется"
          subtitle="Программы, которые делают новую квартиру доступнее уже сегодня."
        />
      </div>

      <Reveal className="mt-10">
        <Marquee
          duration={28}
          items={ticker.map((t) => (
            <span className="flex items-center gap-3 rounded-full border border-line2 bg-elev/60 px-5 py-2.5 text-sm font-semibold text-fg">
              <span className="size-1.5 rounded-full bg-brand" />
              {t}
            </span>
          ))}
        />
      </Reveal>

      <div className="container-x">
        <Reveal stagger className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {promos.map((promo, i) => {
            const c = promoColors[i % promoColors.length]
            return (
              <RevealItem key={promo.title}>
                <Link
                  to={promo.to}
                  className={cn(
                    'group flex h-full flex-col rounded-3xl border border-line bg-elev p-6 transition-all duration-300 hover:-translate-y-1 hover:bg-elev2',
                    c.border,
                  )}
                >
                  <span className={cn('w-fit rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wide', c.tag)}>
                    {promo.tag}
                  </span>
                  <h3 className="mt-5 font-display text-xl leading-tight">
                    {promo.title}
                  </h3>
                  <p className="mt-3 flex-1 text-sm leading-relaxed text-muted">
                    {promo.text}
                  </p>
                  <span className={cn('mt-6 inline-flex items-center gap-1.5 text-sm font-semibold', c.link)}>
                    Подробнее
                    <ArrowUpRight className="size-4 transition-transform duration-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
                  </span>
                </Link>
              </RevealItem>
            )
          })}
        </Reveal>
      </div>
    </section>
  )
}
