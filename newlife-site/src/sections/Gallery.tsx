import { useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { SectionHeading } from '@/components/ui/SectionHeading'
import { gallery, type GalleryCat } from '@/data/site'
import { asset } from '@/lib/asset'
import { cn } from '@/lib/cn'
import { EASE } from '@/lib/motion'

type Filter = 'Все' | GalleryCat
const cats: Filter[] = ['Все', 'Дома', 'Микрорайон', 'Двор и среда', 'Внутри']

// Цвет ярлыка категории — для разнообразия палитры.
const catColor: Record<GalleryCat, string> = {
  'Дома': 'text-brand',
  'Микрорайон': 'text-sky',
  'Двор и среда': 'text-lime',
  'Внутри': 'text-clay',
}

export function Gallery() {
  const [active, setActive] = useState<Filter>('Все')
  const list = useMemo(
    () => (active === 'Все' ? gallery : gallery.filter((g) => g.cat === active)),
    [active],
  )

  return (
    <section id="gallery" className="container-x py-24 md:py-28">
      <SectionHeading
        eyebrow="Галерея проекта"
        title="Как выглядит «Новая Жизнь»"
        subtitle="Реальные фотографии домов и дворов, архитектурные рендеры и виды микрорайона с высоты — выбирайте, что посмотреть."
      />

      <div className="mt-10 flex flex-wrap gap-2">
        {cats.map((c) => (
          <button
            key={c}
            onClick={() => setActive(c)}
            className={cn(
              'rounded-full border px-4 py-2 text-sm font-semibold transition-all duration-300',
              active === c
                ? 'border-brand bg-brand text-on-brand'
                : 'border-line2 bg-elev/60 text-muted hover:text-fg',
            )}
          >
            {c}
          </button>
        ))}
      </div>

      <motion.div
        layout
        className="mt-8 gap-4 [column-fill:_balance] columns-1 sm:columns-2 lg:columns-3 [&>*]:mb-4"
      >
        <AnimatePresence mode="popLayout">
          {list.map((g) => (
            <motion.figure
              key={g.src}
              layout
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.96 }}
              transition={{ duration: 0.4, ease: EASE }}
              className="group relative block break-inside-avoid overflow-hidden rounded-2xl border border-line bg-elev"
            >
              <img
                src={asset(g.src)}
                alt={g.title}
                loading="lazy"
                className="w-full object-cover transition-transform duration-700 ease-[cubic-bezier(0.22,1,0.36,1)] group-hover:scale-[1.06]"
              />
              <span className={cn('absolute left-3 top-3 rounded-full bg-base/90 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide backdrop-blur', catColor[g.cat])}>
                {g.cat}
              </span>
              <figcaption className="pointer-events-none absolute inset-x-0 bottom-0 flex items-end p-4 pt-12 bg-gradient-to-t from-ink/85 via-ink/25 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                <span className="text-sm font-semibold text-[#fdf6ec]">
                  {g.title}
                </span>
              </figcaption>
            </motion.figure>
          ))}
        </AnimatePresence>
      </motion.div>
    </section>
  )
}
