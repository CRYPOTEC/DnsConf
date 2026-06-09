import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { PageHero } from '@/components/PageHero'
import { Reveal, RevealItem } from '@/components/ui/Reveal'
import { ButtonLink } from '@/components/ui/Button'

const programs = [
  { name: 'Семейная ипотека', rate: '6%', note: 'для семей с детьми' },
  { name: 'IT-ипотека', rate: '5%', note: 'для IT-специалистов' },
  { name: 'Господдержка', rate: '8%', note: 'базовая программа' },
  { name: 'Рассрочка', rate: '0%', note: 'от застройщика' },
]

function fmt(n: number) {
  return Math.round(n).toLocaleString('ru-RU')
}

export function Mortgage() {
  const [price, setPrice] = useState(6_200_000)
  const [downPct, setDownPct] = useState(20)
  const [years, setYears] = useState(20)
  const [rate, setRate] = useState(6)

  const { monthly, loan, overpay } = useMemo(() => {
    const down = (price * downPct) / 100
    const loan = price - down
    const r = rate / 100 / 12
    const n = years * 12
    const monthly = r === 0 ? loan / n : (loan * r) / (1 - Math.pow(1 + r, -n))
    const overpay = monthly * n - loan
    return { monthly, loan, overpay }
  }, [price, downPct, years, rate])

  return (
    <>
      <PageHero
        eyebrow="Ипотека"
        title={<>Рассчитайте <span className="text-gradient">платёж</span></>}
        description="Подберём выгодную программу под ваш бюджет. Семейная ипотека от 6%, trade-in и рассрочка от застройщика."
        crumbs={[{ label: 'Ипотека' }]}
      />

      <section className="container-x pb-20">
        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          {/* Калькулятор */}
          <div className="rounded-[2rem] border border-line bg-elev p-7 md:p-9">
            <h2 className="text-2xl md:text-3xl">Калькулятор ипотеки</h2>
            <div className="mt-8 space-y-8">
              <Slider
                label="Стоимость квартиры"
                value={price}
                min={3_000_000}
                max={15_000_000}
                step={100_000}
                onChange={setPrice}
                display={`${fmt(price)} ₽`}
              />
              <Slider
                label="Первоначальный взнос"
                value={downPct}
                min={15}
                max={80}
                step={5}
                onChange={setDownPct}
                display={`${downPct}% · ${fmt((price * downPct) / 100)} ₽`}
              />
              <Slider
                label="Срок кредита"
                value={years}
                min={5}
                max={30}
                step={1}
                onChange={setYears}
                display={`${years} лет`}
              />
              <Slider
                label="Ставка"
                value={rate}
                min={0}
                max={18}
                step={0.5}
                onChange={setRate}
                display={`${rate}%`}
              />
            </div>
          </div>

          {/* Результат */}
          <div className="flex flex-col gap-4 rounded-[2rem] border border-brand/30 bg-gradient-to-b from-elev to-base p-7 md:p-9">
            <p className="text-sm text-muted">Ежемесячный платёж</p>
            <motion.p
              key={Math.round(monthly)}
              initial={{ opacity: 0.4, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="font-display text-4xl text-brand md:text-5xl"
            >
              {fmt(monthly)} ₽
            </motion.p>

            <dl className="mt-4 space-y-3 border-t border-line pt-5 text-sm">
              <Row label="Сумма кредита" value={`${fmt(loan)} ₽`} />
              <Row label="Переплата за весь срок" value={`${fmt(overpay)} ₽`} />
              <Row
                label="Всего к выплате"
                value={`${fmt(loan + overpay)} ₽`}
              />
            </dl>

            <div className="mt-auto pt-6">
              <ButtonLink to="/contacts" className="w-full" magnetic={false}>
                Получить одобрение
              </ButtonLink>
              <p className="mt-3 text-center text-xs text-faint">
                Расчёт предварительный и не является офертой.
              </p>
            </div>
          </div>
        </div>

        {/* Программы */}
        <Reveal stagger className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {programs.map((p) => (
            <RevealItem key={p.name}>
              <button
                onClick={() =>
                  setRate(parseFloat(p.rate) || 0)
                }
                className="w-full rounded-2xl border border-line bg-elev p-5 text-left transition-all duration-300 hover:-translate-y-1 hover:border-brand/50"
              >
                <p className="font-display text-3xl text-brand">{p.rate}</p>
                <p className="mt-2 font-semibold">{p.name}</p>
                <p className="text-xs text-muted">{p.note}</p>
              </button>
            </RevealItem>
          ))}
        </Reveal>
      </section>
    </>
  )
}

function Slider({
  label,
  value,
  min,
  max,
  step,
  onChange,
  display,
}: {
  label: string
  value: number
  min: number
  max: number
  step: number
  onChange: (v: number) => void
  display: string
}) {
  const pct = ((value - min) / (max - min)) * 100
  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <span className="text-sm text-muted">{label}</span>
        <span className="font-display text-base text-fg">{display}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="h-1.5 w-full cursor-pointer appearance-none rounded-full outline-none [&::-webkit-slider-thumb]:size-5 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-base [&::-webkit-slider-thumb]:bg-brand [&::-webkit-slider-thumb]:shadow-[0_0_0_4px_color-mix(in_srgb,var(--color-brand)_25%,transparent)]"
        style={{
          background: `linear-gradient(to right, var(--color-brand) ${pct}%, var(--color-line2) ${pct}%)`,
        }}
      />
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <dt className="text-muted">{label}</dt>
      <dd className="font-semibold text-fg">{value}</dd>
    </div>
  )
}
