import { Phone, Mail, MapPin, Clock } from 'lucide-react'
import { PageHero } from '@/components/PageHero'
import { LeadForm } from '@/components/LeadForm'
import { Reveal } from '@/components/ui/Reveal'
import { company } from '@/data/site'

const contacts = [
  { icon: Phone, label: 'Телефон', value: company.phone, href: company.phoneHref },
  { icon: Mail, label: 'Почта', value: 'info@newlife-ul.ru', href: 'mailto:info@newlife-ul.ru' },
  { icon: MapPin, label: 'Офис продаж', value: `г. ${company.city}, мкр «Новая Жизнь»` },
  { icon: Clock, label: 'Часы работы', value: 'Ежедневно 9:00 – 20:00' },
]

export function Contacts() {
  return (
    <>
      <PageHero
        eyebrow="Контакты"
        title="Свяжитесь с нами"
        description="Приезжайте в офис продаж или оставьте заявку — менеджер «Новой» поможет выбрать квартиру и оформить покупку."
        crumbs={[{ label: 'Контакты' }]}
      />

      <section className="container-x pb-24">
        <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          {/* Контактные данные */}
          <Reveal stagger className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
            {contacts.map((c) => {
              const Icon = c.icon
              const inner = (
                <div className="flex items-start gap-4 rounded-2xl border border-line bg-elev p-5 transition-colors hover:border-brand/40">
                  <span className="grid size-11 shrink-0 place-items-center rounded-xl bg-brand/10 text-brand">
                    <Icon className="size-5" />
                  </span>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-faint">
                      {c.label}
                    </p>
                    <p className="mt-1 font-semibold text-fg">{c.value}</p>
                  </div>
                </div>
              )
              return c.href ? (
                <a key={c.label} href={c.href} className="block">
                  {inner}
                </a>
              ) : (
                <div key={c.label}>{inner}</div>
              )
            })}
          </Reveal>

          {/* Форма */}
          <Reveal direction="left">
            <div className="rounded-[2rem] border border-line bg-elev p-7 md:p-9">
              <h2 className="text-2xl md:text-3xl">Оставить заявку</h2>
              <p className="mt-2 text-sm text-muted">
                Перезвоним в течение рабочего дня.
              </p>
              <div className="mt-6">
                <LeadForm />
              </div>
            </div>
          </Reveal>
        </div>

        {/* Карта-заглушка */}
        <Reveal className="mt-6">
          <div className="relative h-72 overflow-hidden rounded-[2rem] border border-line bg-elev">
            <div className="absolute inset-0 bg-grid opacity-30" />
            <div className="absolute inset-0 grid place-items-center">
              <div className="flex flex-col items-center gap-3 text-center">
                <span className="relative grid size-14 place-items-center">
                  <span className="absolute inset-0 animate-ping rounded-full bg-brand/30" />
                  <span className="relative grid size-11 place-items-center rounded-full bg-brand text-on-brand">
                    <MapPin className="size-6" />
                  </span>
                </span>
                <p className="font-display text-lg">
                  г. {company.city}, микрорайон «Новая Жизнь»
                </p>
                <p className="text-sm text-muted">
                  Офис продаж · парковка для гостей
                </p>
              </div>
            </div>
          </div>
        </Reveal>
      </section>
    </>
  )
}
