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

const icons: Record<string, LucideIcon> = {
  ShieldCheck,
  Trees,
  KeyRound,
  Percent,
  Building2,
  HeartHandshake,
}

export function Advantages() {
  return (
    <section className="container-x py-24 md:py-28">
      <SectionHeading
        eyebrow="Почему «Новая»"
        title="Не просто строим дома — создаём среду"
        subtitle="Наша миссия — качественная недвижимость, которая делает жизнь лучше."
      />
      <Reveal stagger className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {advantages.map((adv) => {
          const Icon = icons[adv.icon] ?? ShieldCheck
          return (
            <RevealItem key={adv.title}>
              <div className="group relative h-full overflow-hidden rounded-3xl border border-line bg-elev p-7 transition-colors duration-300 hover:border-line2">
                <div className="absolute -right-12 -top-12 size-32 rounded-full bg-brand/5 blur-2xl transition-all duration-500 group-hover:bg-brand/15" />
                <span className="relative grid size-12 place-items-center rounded-2xl border border-line2 bg-base text-brand transition-transform duration-300 group-hover:-translate-y-1">
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
