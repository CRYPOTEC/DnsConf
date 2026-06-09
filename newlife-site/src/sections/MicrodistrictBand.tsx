import { motion } from 'framer-motion'
import { ArrowUpRight, Trees, Car, GraduationCap } from 'lucide-react'
import { ButtonLink } from '@/components/ui/Button'
import { asset } from '@/lib/asset'
import { EASE } from '@/lib/motion'

const points = [
  { icon: Car, text: 'Дворы без машин' },
  { icon: Trees, text: 'Парки и зелёные зоны' },
  { icon: GraduationCap, text: 'Школы и детские сады' },
]

const cutoutOutline =
  'drop-shadow(0 1.5px 0 var(--color-brand)) drop-shadow(0 -1.5px 0 var(--color-brand)) drop-shadow(1.5px 0 0 var(--color-brand)) drop-shadow(-1.5px 0 0 var(--color-brand)) drop-shadow(0 30px 44px rgba(0,0,0,0.5))'

export function MicrodistrictBand() {
  return (
    <section className="relative overflow-hidden py-28 md:py-36">
      {/* Фон — реальные улицы микрорайона */}
      <div className="absolute inset-0 -z-10">
        <img
          src={asset('/img/street-towers.jpg')}
          alt=""
          className="size-full object-cover"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-ink/95 via-ink/75 to-ink/35" />
        <div className="absolute inset-0 bg-gradient-to-t from-ink/85 to-transparent" />
      </div>

      <div className="container-x grid items-center gap-12 lg:grid-cols-[1.1fr_0.9fr]">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.7, ease: EASE }}
        >
          <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[#a7c957] backdrop-blur">
            <span className="size-1.5 rounded-full bg-[#a7c957]" />
            Среда для жизни
          </span>
          <h2 className="mt-5 text-4xl text-[#fdf6ec] sm:text-5xl md:text-6xl">
            Целый микрорайон,
            <br />а не просто дом
          </h2>
          <p className="mt-5 max-w-md text-base leading-relaxed text-[#d9ccb6] sm:text-lg">
            «Новая Жизнь» — это продуманная среда: дворы без машин, парки, школы
            и детские сады, магазины и сервисы на первых этажах. Всё необходимое —
            в шаговой доступности от дома.
          </p>

          <ul className="mt-7 flex flex-wrap gap-x-6 gap-y-3">
            {points.map((p) => {
              const Icon = p.icon
              return (
                <li
                  key={p.text}
                  className="flex items-center gap-2 text-sm font-semibold text-[#ece1cf]"
                >
                  <Icon className="size-4 text-[#a7c957]" />
                  {p.text}
                </li>
              )
            })}
          </ul>

          <div className="mt-9">
            <ButtonLink to="/newlife">
              Смотреть проект
              <ArrowUpRight className="size-4 transition-transform duration-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
            </ButtonLink>
          </div>
        </motion.div>

        {/* «Вырезанный» дом с контуром */}
        <motion.div
          initial={{ opacity: 0, scale: 0.94 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.9, ease: EASE }}
          className="relative hidden justify-center lg:flex"
        >
          <motion.img
            src={asset('/img/cut-tower-medallion.webp')}
            alt="Жилой дом микрорайона «Новая Жизнь»"
            animate={{ y: [0, -12, 0] }}
            transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut' }}
            className="max-h-[460px] w-auto"
            style={{ filter: cutoutOutline }}
          />
        </motion.div>
      </div>
    </section>
  )
}
