import { ButtonLink } from '@/components/ui/Button'

export function NotFound() {
  return (
    <section className="relative grid min-h-[70vh] place-items-center overflow-hidden px-6 pt-32">
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-grid opacity-30 mask-fade-b" />
        <div className="absolute left-1/2 top-1/3 size-96 -translate-x-1/2 rounded-full bg-brand/15 blur-[120px]" />
      </div>
      <div className="text-center">
        <p className="font-display text-7xl text-gradient md:text-9xl">404</p>
        <h1 className="mt-4 text-2xl md:text-3xl">Страница не найдена</h1>
        <p className="mx-auto mt-3 max-w-md text-muted">
          Возможно, она переехала в новый дом. Вернитесь на главную и продолжите
          выбор квартиры.
        </p>
        <div className="mt-8 flex justify-center gap-4">
          <ButtonLink to="/">На главную</ButtonLink>
          <ButtonLink to="/apartments" variant="outline">
            Выбрать квартиру
          </ButtonLink>
        </div>
      </div>
    </section>
  )
}
