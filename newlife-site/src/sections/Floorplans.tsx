import { ArrowUpRight } from 'lucide-react'
import { SectionHeading } from '@/components/ui/SectionHeading'
import { Reveal, RevealItem } from '@/components/ui/Reveal'
import { ButtonLink } from '@/components/ui/Button'
import { floorplans } from '@/data/site'
import { asset } from '@/lib/asset'

export function Floorplans() {
  return (
    <section id="plans" className="container-x py-24 md:py-28">
      <SectionHeading
        eyebrow="Планировки"
        title="Реальные планировки квартир"
        subtitle="От студий до просторных трёхкомнатных — со свободными планировками и чистовой отделкой «под ключ»."
      />

      <Reveal stagger className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {floorplans.map((fp) => (
          <RevealItem key={fp.src}>
            <div className="group h-full overflow-hidden rounded-3xl border border-line bg-elev transition-colors duration-300 hover:border-sky/50">
              <div className="relative aspect-[4/3] overflow-hidden bg-white p-5">
                <img
                  src={asset(fp.src)}
                  alt={`Планировка — ${fp.rooms}, ${fp.area}`}
                  loading="lazy"
                  className="size-full object-contain transition-transform duration-500 group-hover:scale-[1.06]"
                />
                <span className="absolute left-3 top-3 rounded-full bg-sky/15 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide text-sky">
                  {fp.rooms}
                </span>
              </div>
              <div className="flex items-center justify-between border-t border-line p-5">
                <span className="font-display text-lg">{fp.area}</span>
                <span className="text-sm text-muted">отделка под ключ</span>
              </div>
            </div>
          </RevealItem>
        ))}
      </Reveal>

      <Reveal className="mt-10">
        <ButtonLink to="/apartments">
          Все планировки и цены
          <ArrowUpRight className="size-4 transition-transform duration-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
        </ButtonLink>
      </Reveal>
    </section>
  )
}
