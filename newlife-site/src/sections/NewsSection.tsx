import { ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { SectionHeading } from '@/components/ui/SectionHeading'
import { Reveal, RevealItem } from '@/components/ui/Reveal'
import { news } from '@/data/site'

export function NewsSection() {
  return (
    <section className="container-x py-24 md:py-28">
      <div className="flex flex-wrap items-end justify-between gap-6">
        <SectionHeading
          eyebrow="Новости"
          title="Что происходит в «Новой»"
          className="mb-0"
        />
        <Link
          to="/about"
          className="group inline-flex items-center gap-1.5 text-sm font-semibold text-brand"
        >
          Все новости
          <ArrowUpRight className="size-4 transition-transform duration-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
        </Link>
      </div>

      <Reveal stagger className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
        {news.map((item) => (
          <RevealItem key={item.title}>
            <article className="group flex h-full flex-col rounded-3xl border border-line bg-elev p-6 transition-all duration-300 hover:-translate-y-1 hover:border-brand/40">
              <div className="flex items-center justify-between text-xs">
                <span className="rounded-full bg-base px-2.5 py-1 font-semibold text-brand">
                  {item.tag}
                </span>
                <time className="text-faint">{item.date}</time>
              </div>
              <h3 className="mt-5 flex-1 font-display text-lg leading-snug">
                {item.title}
              </h3>
              <span className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-muted transition-colors group-hover:text-brand">
                Читать
                <ArrowUpRight className="size-4" />
              </span>
            </article>
          </RevealItem>
        ))}
      </Reveal>
    </section>
  )
}
