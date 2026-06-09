import { Link } from 'react-router-dom'
import { Phone, MapPin, Mail } from 'lucide-react'
import { company, nav } from '@/data/site'
import { Logo } from './Navbar'

export function Footer() {
  return (
    <footer className="relative mt-24 border-t border-line bg-ink">
      <div className="container-x py-16">
        <div className="grid gap-12 md:grid-cols-[1.4fr_1fr_1fr]">
          <div>
            <Link to="/" className="flex items-center gap-2.5">
              <Logo />
              <span className="font-display text-xl font-bold">Новая</span>
            </Link>
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-muted">
              Создаём пространства, где хочется жить. Квартиры в новостройках
              {' '}
              {company.city}а с отделкой и продуманной средой.
            </p>
            <div className="mt-6 flex flex-wrap gap-4 text-sm">
              <a
                href={company.phoneHref}
                className="flex items-center gap-2 font-semibold text-fg transition-colors hover:text-brand"
              >
                <Phone className="size-4 text-brand" />
                {company.phone}
              </a>
            </div>
          </div>

          <div>
            <h3 className="font-display text-sm uppercase tracking-[0.18em] text-faint">
              Навигация
            </h3>
            <ul className="mt-4 space-y-2.5 text-sm">
              {nav.map((item) => (
                <li key={item.to}>
                  <Link
                    to={item.to}
                    className="text-muted transition-colors hover:text-brand"
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="font-display text-sm uppercase tracking-[0.18em] text-faint">
              Контакты
            </h3>
            <ul className="mt-4 space-y-3 text-sm text-muted">
              <li className="flex items-start gap-2">
                <MapPin className="mt-0.5 size-4 shrink-0 text-brand" />
                г. {company.city}, офис продаж «Новая Жизнь»
              </li>
              <li className="flex items-start gap-2">
                <Mail className="mt-0.5 size-4 shrink-0 text-brand" />
                info@newlife-ul.ru
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 flex flex-col gap-4 border-t border-line pt-6 text-xs text-faint md:flex-row md:items-center md:justify-between">
          <p>
            © {new Date().getFullYear()} ГК «Новая». Работаем с {company.since}{' '}
            года.
          </p>
          <p className="text-faint">
            Не является публичной офертой. Концепт-редизайн.
          </p>
        </div>
      </div>
    </footer>
  )
}
