import { motion } from 'framer-motion'
import { ArrowUpRight, Sparkles } from 'lucide-react'
import { ButtonLink } from '@/components/ui/Button'
import { company } from '@/data/site'
import { EASE } from '@/lib/motion'
import { asset } from '@/lib/asset'

const word = {
  hidden: { opacity: 0, y: '0.6em' },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.15 + i * 0.08, duration: 0.8, ease: EASE },
  }),
}

const titleWords = ['Пространства,', 'где', 'хочется', 'жить']

// Контур терракотового цвета вокруг «вырезанного» дома + мягкая тень.
const cutoutOutline =
  'drop-shadow(0 1.5px 0 var(--color-brand)) drop-shadow(0 -1.5px 0 var(--color-brand)) drop-shadow(1.5px 0 0 var(--color-brand)) drop-shadow(-1.5px 0 0 var(--color-brand)) drop-shadow(0 32px 46px rgba(60,30,15,0.45))'

export function Hero() {
  return (
    <section className="relative overflow-hidden pt-32 pb-20 md:pt-40 md:pb-28">
      {/* Фон — реальный микрорайон «Новая Жизнь» с высоты */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <img
          src={asset('/img/aerial-summer.jpg')}
          alt=""
          className="size-full object-cover"
        />
        {/* кремовая вуаль для читаемости текста слева */}
        <div className="absolute inset-0 bg-[linear-gradient(105deg,var(--color-base)_0%,var(--color-base)_36%,color-mix(in_srgb,var(--color-base)_80%,transparent)_50%,color-mix(in_srgb,var(--color-base)_28%,transparent)_68%,transparent_84%)]" />
        {/* общий лёгкий слой + затухание сверху/снизу к фону страницы */}
        <div className="absolute inset-0 bg-base/30 lg:bg-base/10" />
        <div className="absolute inset-0 bg-gradient-to-b from-base via-transparent to-base" />
        <div className="absolute inset-0 bg-grid opacity-[0.12] mask-fade-b" />
      </div>

      <div className="container-x grid items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]">
        <div>
          <motion.span
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 rounded-full border border-line2 bg-elev/70 px-3.5 py-1.5 text-xs font-semibold tracking-tight text-brand backdrop-blur"
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

/** «Вырезанные» дома микрорайона с терракотовым контуром + чипы со статистикой. */
function HeroVisual() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, duration: 1, ease: EASE }}
      className="relative mx-auto hidden w-full max-w-xl lg:block"
    >
      <motion.img
        src={asset('/img/cut-towers-twin.webp')}
        alt="Дома микрорайона «Новая Жизнь»"
        animate={{ y: [0, -12, 0] }}
        transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut' }}
        className="w-full"
        style={{ filter: cutoutOutline }}
      />

      <motion.div
        animate={{ y: [0, -10, 0] }}
        transition={{ duration: 5.5, repeat: Infinity, ease: 'easeInOut' }}
        className="absolute -right-2 top-2 glass rounded-2xl px-4 py-3 shadow-[0_18px_50px_-24px_rgba(70,40,20,0.5)]"
      >
        <p className="text-xs text-muted">Построено</p>
        <p className="font-display text-lg text-brand">1,5 млн м²</p>
      </motion.div>
      <motion.div
        animate={{ y: [0, 10, 0] }}
        transition={{ duration: 6.5, repeat: Infinity, ease: 'easeInOut', delay: 0.4 }}
        className="absolute -left-3 bottom-6 glass rounded-2xl px-4 py-3 shadow-[0_18px_50px_-24px_rgba(70,40,20,0.5)]"
      >
        <p className="text-xs text-muted">Опыт</p>
        <p className="font-display text-lg">18+ лет</p>
      </motion.div>
    </motion.div>
  )
}
