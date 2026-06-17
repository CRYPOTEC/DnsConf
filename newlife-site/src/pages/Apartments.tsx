import { useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { ArrowUpRight } from 'lucide-react'
import { PageHero } from '@/components/PageHero'
import { ButtonLink } from '@/components/ui/Button'
import { cn } from '@/lib/cn'
import { EASE } from '@/lib/motion'
import { asset } from '@/lib/asset'

type Flat = {
  id: number
  rooms: number
  area: number
  price: number
  project: 'Новая Жизнь' | 'Новая Наганова'
  floor: number
  plan: string
}

const flats: Flat[] = [
  { id: 1, rooms: 1, area: 38.4, price: 4.1, project: 'Новая Жизнь', floor: 4, plan: '/img/plans/plan11.jpg' },
  { id: 2, rooms: 1, area: 42.1, price: 4.6, project: 'Новая Наганова', floor: 9, plan: '/img/plans/plan3.jpg' },
  { id: 3, rooms: 2, area: 56.8, price: 6.2, project: 'Новая Жизнь', floor: 7, plan: '/img/plans/plan8.jpg' },
  { id: 4, rooms: 2, area: 61.3, price: 6.8, project: 'Новая Наганова', floor: 12, plan: '/img/plans/plan7.jpg' },
  { id: 5, rooms: 3, area: 78.5, price: 8.9, project: 'Новая Жизнь', floor: 5, plan: '/img/plans/plan4.jpg' },
  { id: 6, rooms: 3, area: 84.2, price: 9.7, project: 'Новая Наганова', floor: 14, plan: '/img/plans/plan12.jpg' },
  { id: 7, rooms: 1, area: 36.0, price: 3.9, project: 'Новая Наганова', floor: 3, plan: '/img/plans/plan13.jpg' },
  { id: 8, rooms: 2, area: 54.0, price: 5.9, project: 'Новая Жизнь', floor: 10, plan: '/img/plans/plan9.jpg' },
  { id: 9, rooms: 4, area: 102.6, price: 12.4, project: 'Новая Наганова', floor: 16, plan: '/img/plans/plan10.jpg' },
]

const filters = [
  { label: 'Все', value: 0 },
  { label: 'Студии и 1к', value: 1 },
  { label: '2-комнатные', value: 2 },
  { label: '3-комнатные', value: 3 },
  { label: '4+ комнат', value: 4 },
]

export function Apartments() {
  const [active, setActive] = useState(0)

  const list = useMemo(
    () => (active === 0 ? flats : flats.filter((f) => f.rooms === active)),
    [active],
  )

  return (
    <>
      <PageHero
        eyebrow="Каталог"
        title="Выберите квартиру"
        description="Свободные планировки в «Новой Жизни» и «Новой Нагановой». Цены актуальны, отделка под ключ, доступна семейная ипотека от 6%."
        crumbs={[{ label: 'Квартиры' }]}
      />

      <section className="container-x pb-24">
        {/* Фильтр */}
        <div className="mb-10 flex flex-wrap gap-2">
          {filters.map((f) => (
            <button
              key={f.value}
              onClick={() => setActive(f.value)}
              className={cn(
                'rounded-full border px-4 py-2 text-sm font-semibold transition-all duration-300',
                active === f.value
                  ? 'border-brand bg-brand text-on-brand'
                  : 'border-line2 bg-elev/50 text-muted hover:text-fg',
              )}
            >
              {f.label}
            </button>
          ))}
        </div>

        <motion.div layout className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <AnimatePresence mode="popLayout">
            {list.map((flat) => (
              <motion.article
                key={flat.id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.35, ease: EASE }}
                className="group flex flex-col overflow-hidden rounded-3xl border border-line bg-elev transition-colors duration-300 hover:border-brand/50"
              >
                <FlatPlan plan={flat.plan} rooms={flat.rooms} />
                <div className="flex flex-1 flex-col p-6">
                  <div className="flex items-center justify-between">
                    <span className="rounded-full bg-base px-3 py-1 text-xs font-semibold text-muted">
                      {flat.project}
                    </span>
                    <span className="text-xs text-faint">{flat.floor} этаж</span>
                  </div>
                  <h3 className="mt-4 font-display text-2xl">
                    {flat.rooms}-комн. · {flat.area} м²
                  </h3>
                  <p className="mt-1 text-sm text-muted">
                    от{' '}
                    <span className="font-bold text-brand">
                      {flat.price.toLocaleString('ru-RU')} млн ₽
                    </span>
                  </p>
                  <div className="mt-auto pt-6">
                    <ButtonLink
                      to="/contacts"
                      variant="outline"
                      magnetic={false}
                      className="w-full"
                    >
                      Узнать подробнее
                      <ArrowUpRight className="size-4" />
                    </ButtonLink>
                  </div>
                </div>
              </motion.article>
            ))}
          </AnimatePresence>
        </motion.div>
      </section>
    </>
  )
}

/** Реальная планировка квартиры. */
function FlatPlan({ plan, rooms }: { plan: string; rooms: number }) {
  return (
    <div className="relative aspect-[16/10] overflow-hidden border-b border-line bg-white p-4">
      <img
        src={asset(plan)}
        alt={`Планировка ${rooms}-комнатной квартиры`}
        loading="lazy"
        className="size-full object-contain transition-transform duration-500 group-hover:scale-105"
      />
    </div>
  )
}
