import { Reveal } from '@/components/ui/Reveal'
import { LeadForm } from '@/components/LeadForm'
import { company } from '@/data/site'

export function CTASection() {
  return (
    <section id="cta" className="container-x py-24 md:py-28">
      <Reveal>
        <div className="relative overflow-hidden rounded-[2rem] border border-line bg-elev p-8 md:p-12">
          {/* фоновое свечение и сетка */}
          <div className="pointer-events-none absolute inset-0 bg-grid opacity-30" />
          <div className="pointer-events-none absolute -left-20 -top-20 size-72 rounded-full bg-brand/20 blur-[100px]" />
          <div className="pointer-events-none absolute -bottom-24 right-0 size-72 rounded-full bg-sky/15 blur-[100px]" />

          <div className="relative grid items-center gap-10 lg:grid-cols-[1fr_1fr]">
            <div>
              <h2 className="text-3xl sm:text-4xl md:text-5xl">
                Подберём квартиру <span className="text-gradient">мечты</span>
              </h2>
              <p className="mt-4 max-w-md text-base leading-relaxed text-muted">
                Оставьте заявку — расскажем про свободные планировки, актуальные
                акции и рассчитаем ипотеку под ваш бюджет. Перезвоним в течение
                рабочего дня.
              </p>
              <a
                href={company.phoneHref}
                className="mt-6 inline-block font-display text-2xl text-brand transition-opacity hover:opacity-80"
              >
                {company.phone}
              </a>
            </div>

            <div className="rounded-2xl border border-line bg-base/60 p-6 backdrop-blur">
              <LeadForm />
            </div>
          </div>
        </div>
      </Reveal>
    </section>
  )
}
