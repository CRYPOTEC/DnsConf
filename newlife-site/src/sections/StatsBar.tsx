import { AnimatedCounter } from '@/components/ui/AnimatedCounter'
import { Reveal, RevealItem } from '@/components/ui/Reveal'
import { stats } from '@/data/site'

export function StatsBar() {
  return (
    <section className="container-x">
      <Reveal
        stagger
        className="grid grid-cols-2 gap-px overflow-hidden rounded-3xl border border-line bg-line lg:grid-cols-4"
      >
        {stats.map((s) => (
          <RevealItem
            key={s.label}
            className="bg-elev px-6 py-8 text-center transition-colors duration-300 hover:bg-elev2"
          >
            <div className="font-display text-4xl text-fg md:text-5xl">
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
  )
}
