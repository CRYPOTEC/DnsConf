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

/** Витрина с реальным видом микрорайона и фрагментом фасада. */
function HeroVisual() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.3, duration: 1, ease: EASE }}
      className="relative mx-auto w-full max-w-xl"
    >
      <motion.div
        animate={{ y: [0, -12, 0] }}
        transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut' }}
        className="relative"
      >
        {/* Тёплая подсветка под карточкой */}
        <div className="absolute -inset-6 -z-10 rounded-[3rem] bg-[radial-gradient(60%_60%_at_60%_30%,color-mix(in_srgb,var(--color-brand)_22%,transparent),transparent_70%)]" />

        {/* Главный кадр — генплан микрорайона */}
        <figure className="overflow-hidden rounded-[2.25rem] border border-line bg-elev p-2 shadow-[0_40px_90px_-40px_rgba(70,40,20,0.45)] glow-brand">
          <img
            src={asset('/img/complex-aerial.jpg')}
            alt="Микрорайон «Новая Жизнь» — вид сверху на кварталы у воды"
            className="aspect-[5/4] w-full rounded-[1.7rem] object-cover"
            loading="eager"
          />
        </figure>

        {/* Парящий фрагмент фасада */}
        <motion.figure
          animate={{ y: [0, 12, 0] }}
          transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut', delay: 0.6 }}
          className="absolute -bottom-8 -left-6 hidden w-40 overflow-hidden rounded-2xl border border-line bg-elev p-1.5 shadow-[0_24px_60px_-30px_rgba(70,40,20,0.5)] sm:block"
        >
          <img
            src={asset('/img/facade-terracotta.jpg')}
            alt="Терракотовый фасад дома «Новой Жизни»"
            className="aspect-square w-full rounded-xl object-cover"
            loading="lazy"
          />
        </motion.figure>

        {/* Чип со статистикой */}
        <motion.div
          animate={{ y: [0, -10, 0] }}
          transition={{ duration: 5.5, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute -right-3 top-8 glass rounded-2xl px-4 py-3 shadow-[0_18px_50px_-24px_rgba(70,40,20,0.45)]"
        >
          <p className="text-xs text-muted">Построено</p>
          <p className="font-display text-lg text-brand">1,5 млн м²</p>
        </motion.div>
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 6.5, repeat: Infinity, ease: 'easeInOut', delay: 0.4 }}
          className="absolute right-6 -bottom-6 glass rounded-2xl px-4 py-3 shadow-[0_18px_50px_-24px_rgba(70,40,20,0.45)]"
        >
          <p className="text-xs text-muted">Опыт</p>
          <p className="font-display text-lg">18+ лет</p>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}
