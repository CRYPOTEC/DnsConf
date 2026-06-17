import {
  ShieldCheck,
  Trees,
  KeyRound,
  Percent,
  Building2,
  HeartHandshake,
  type LucideIcon,
} from 'lucide-react'
import { SectionHeading } from '@/components/ui/SectionHeading'
import { Reveal, RevealItem } from '@/components/ui/Reveal'
import { advantages } from '@/data/site'
import { cn } from '@/lib/cn'

const icons: Record<string, LucideIcon> = {
  ShieldCheck,
  Trees,
  KeyRound,
  Percent,
  Building2,
  HeartHandshake,
}

// Разные акцентные цвета (с фасадов проекта): терракота, зелёный, синий, глина.
const accents = [
  { icon: 'text-brand', glow: 'bg-brand/5 group-hover:bg-brand/15' },
  { icon: 'text-lime', glow: 'bg-lime/5 group-hover:bg-lime/20' },
  { icon: 'text-sky', glow: 'bg-sky/5 group-hover:bg-sky/20' },
  { icon: 'text-clay', glow: 'bg-clay/5 group-hover:bg-clay/15' },
  { icon: 'text-brand', glow: 'bg-brand/5 group-hover:bg-brand/15' },
  { icon: 'text-lime', glow: 'bg-lime/5 group-hover:bg-lime/20' },
]

export function Advantages() {
  return (
    <section className="container-x py-24 md:py-28">
      <SectionHeading
        eyebrow="Почему «Новая»"
        title="Не просто строим дома — создаём среду"
        subtitle="Наша миссия — качественная недвижимость, которая делает жизнь лучше."
      />
      <Reveal stagger className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {advantages.map((adv, i) => {
          const Icon = icons[adv.icon] ?? ShieldCheck
          const a = accents[i % accents.length]
          return (
            <RevealItem key={adv.title}>
              <div className="group relative h-full overflow-hidden rounded-3xl border border-line bg-elev p-7 transition-colors duration-300 hover:border-line2">
                <div className={cn('absolute -right-12 -top-12 size-32 rounded-full blur-2xl transition-all duration-500', a.glow)} />
                <span className={cn('relative grid size-12 place-items-center rounded-2xl border border-line2 bg-base transition-transform duration-300 group-hover:-translate-y-1', a.icon)}>
                  <Icon className="size-6" />
                </span>
                <h3 className="relative mt-5 font-display text-xl">{adv.title}</h3>
                <p className="relative mt-3 text-sm leading-relaxed text-muted">
                  {adv.text}
                </p>
              </div>
            </RevealItem>
          )
        })}
      </Reveal>
    </section>
  )
}
