import { motion } from 'framer-motion'
import { ArrowUpRight, Sparkles } from 'lucide-react'
import { ButtonLink } from '@/components/ui/Button'
import { company } from '@/data/site'
import { EASE } from '@/lib/motion'

const word = {
  hidden: { opacity: 0, y: '0.6em' },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.15 + i * 0.08, duration: 0.8, ease: EASE },
  }),
}

const titleWords = ['Пространства,', 'где', 'хочется', 'жить']

export function Hero() {
  return (
    <section className="relative overflow-hidden pt-32 pb-20 md:pt-40 md:pb-28">
      {/* Фон: сетка + мягкие световые пятна */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-grid opacity-[0.4] mask-fade-b" />
        <motion.div
          className="absolute -top-40 left-1/2 size-[640px] -translate-x-1/2 rounded-full blur-[120px]"
          style={{ background: 'radial-gradient(circle, color-mix(in srgb, var(--color-brand) 35%, transparent), transparent 70%)' }}
          animate={{ scale: [1, 1.15, 1], opacity: [0.5, 0.7, 0.5] }}
          transition={{ duration: 9, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute right-[-10%] top-1/3 size-[420px] rounded-full blur-[120px]"
          style={{ background: 'radial-gradient(circle, color-mix(in srgb, var(--color-sky) 28%, transparent), transparent 70%)' }}
          animate={{ scale: [1, 1.2, 1], opacity: [0.35, 0.55, 0.35] }}
          transition={{ duration: 11, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
        />
      </div>

      <div className="container-x grid items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]">
        <div>
          <motion.span
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 rounded-full border border-line2 bg-elev/60 px-3.5 py-1.5 text-xs font-semibold tracking-tight text-brand backdrop-blur"
          >
            <Sparkles className="size-3.5" />
            Застройщик №1 в {company.city}е по версии жителей
          </motion.span>

          <h1 className="mt-6 text-5xl leading-[0.98] sm:text-6xl md:text-7xl">
            {titleWords.map((w, i) => (
              <span key={i} className="mr-[0.25em] inline-block overflow-hidden align-bottom">
                <motion.span
                  custom={i}
                  variants={word}
                  initial="hidden"
                  animate="show"
                  className={i >= 2 ? 'inline-block text-gradient' : 'inline-block'}
                >
                  {w}
                </motion.span>
              </span>
            ))}
          </h1>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.8 }}
            className="mt-6 max-w-xl text-lg leading-relaxed text-muted"
          >
            Квартиры с отделкой в современных микрорайонах «Новая Жизнь» и «Новая
            Наганова». Дворы без машин, парки и вся инфраструктура счастливой
            жизни рядом с домом.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.75, duration: 0.7 }}
            className="mt-9 flex flex-wrap items-center gap-4"
          >
            <ButtonLink to="/apartments">
              Выбрать квартиру
              <ArrowUpRight className="size-4 transition-transform duration-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
            </ButtonLink>
            <ButtonLink to="/mortgage" variant="outline">
              Рассчитать ипотеку
            </ButtonLink>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1, duration: 0.8 }}
            className="mt-10 flex items-center gap-6 text-sm text-faint"
          >
            <span className="flex items-center gap-2">
              <span className="size-2 rounded-full bg-brand" /> Семейная ипотека
              от 6%
            </span>
            <span className="hidden h-4 w-px bg-line2 sm:block" />
            <span className="hidden sm:inline">Отделка под ключ</span>
          </motion.div>
        </div>

        <HeroVisual />
      </div>
    </section>
  )
}

/** Парящий изометрический «дом» с орбитами и бликами. */
function HeroVisual() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.3, duration: 1, ease: EASE }}
      className="relative mx-auto aspect-square w-full max-w-md"
    >
      <motion.div
        animate={{ y: [0, -16, 0] }}
        transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
        className="relative size-full"
      >
        {/* Орбитальные кольца */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 40, repeat: Infinity, ease: 'linear' }}
          className="absolute inset-0 rounded-full border border-line2/60"
        />
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 28, repeat: Infinity, ease: 'linear' }}
          className="absolute inset-8 rounded-full border border-dashed border-line2/40"
        />

        {/* Стеклянная подложка */}
        <div className="absolute inset-10 rounded-[2.5rem] glass glow-brand" />

        {/* SVG-здания */}
        <svg
          viewBox="0 0 200 200"
          className="absolute inset-0 size-full drop-shadow-[0_30px_60px_rgba(0,0,0,0.5)]"
        >
          <defs>
            <linearGradient id="b1" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#1a2530" />
              <stop offset="100%" stopColor="#0e151c" />
            </linearGradient>
            <linearGradient id="b2" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#2fe0a6" />
              <stop offset="100%" stopColor="#1aa37a" />
            </linearGradient>
          </defs>
          {/* задние корпуса */}
          <rect x="58" y="74" width="34" height="86" rx="5" fill="url(#b1)" />
          <rect x="116" y="64" width="30" height="96" rx="5" fill="url(#b1)" />
          {/* центральный акцентный корпус */}
          <rect x="86" y="52" width="34" height="108" rx="6" fill="url(#b2)" />
          {/* окна (мерцают) */}
          {Array.from({ length: 6 }).map((_, r) =>
            Array.from({ length: 2 }).map((__, c) => (
              <motion.rect
                key={`${r}-${c}`}
                x={92 + c * 13}
                y={62 + r * 15}
                width="8"
                height="9"
                rx="1.5"
                fill="#06181a"
                animate={{ opacity: [0.35, 1, 0.35] }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  delay: (r + c) * 0.4,
                  ease: 'easeInOut',
                }}
              />
            )),
          )}
        </svg>

        {/* Парящая инфо-метка */}
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute -right-2 top-6 glass rounded-2xl px-4 py-3"
        >
          <p className="text-xs text-muted">Построено</p>
          <p className="font-display text-lg text-brand">1,5 млн м²</p>
        </motion.div>
        <motion.div
          animate={{ y: [0, -12, 0] }}
          transition={{ duration: 5.5, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
          className="absolute -left-3 bottom-10 glass rounded-2xl px-4 py-3"
        >
          <p className="text-xs text-muted">Опыт</p>
          <p className="font-display text-lg">18+ лет</p>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}
