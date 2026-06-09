import { Link } from 'react-router-dom'
import { Phone, MapPin, Mail } from 'lucide-react'
import { company, nav } from '@/data/site'
import { Logo } from './Navbar'

export function Footer() {
  return (
    <footer className="relative mt-24 bg-ink text-[#ece1cf]">
      <div className="container-x py-16">
        <div className="grid gap-12 md:grid-cols-[1.4fr_1fr_1fr]">
          <div>
            <Link to="/" className="flex items-center gap-2.5">
              <Logo />
              <span className="font-display text-xl font-bold text-[#fdf6ec]">
                {company.name}
              </span>
            </Link>
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-[#b6a78f]">
              Создаём пространства, где хочется жить. Квартиры в новостройках
              {' '}
              {company.city}а с отделкой и продуманной средой.
            </p>
            <div className="mt-6 flex flex-wrap gap-4 text-sm">
              <a
                href={company.phoneHref}
                className="flex items-center gap-2 font-semibold text-[#fdf6ec] transition-colors hover:text-brand-2"
              >
                <Phone className="size-4 text-brand-2" />
                {company.phone}
              </a>
            </div>
          </div>

          <div>
            <h3 className="font-display text-sm uppercase tracking-[0.18em] text-[#8d7f6a]">
              Навигация
            </h3>
            <ul className="mt-4 space-y-2.5 text-sm">
              {nav.map((item) => (
                <li key={item.to}>
                  <Link
                    to={item.to}
                    className="text-[#c7b9a1] transition-colors hover:text-brand-2"
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="font-display text-sm uppercase tracking-[0.18em] text-[#8d7f6a]">
              Контакты
            </h3>
            <ul className="mt-4 space-y-3 text-sm text-[#c7b9a1]">
              <li className="flex items-start gap-2">
                <MapPin className="mt-0.5 size-4 shrink-0 text-brand-2" />
                г. {company.city}, офис продаж «Новая Жизнь»
              </li>
              <li className="flex items-start gap-2">
                <Mail className="mt-0.5 size-4 shrink-0 text-brand-2" />
                info@newlife-ul.ru
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 flex flex-col gap-4 border-t border-white/10 pt-6 text-xs text-[#8d7f6a] md:flex-row md:items-center md:justify-between">
          <p>
            © {new Date().getFullYear()} ГК «Новая Жизнь». Работаем с{' '}
            {company.since} года.
          </p>
          <p>Не является публичной офертой. Концепт-редизайн.</p>
        </div>
      </div>
    </footer>
  )
}
