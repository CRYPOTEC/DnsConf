import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Check, Loader2 } from 'lucide-react'
import { Button } from './ui/Button'

type Props = { compact?: boolean }

export function LeadForm({ compact = false }: Props) {
  const [state, setState] = useState<'idle' | 'loading' | 'done'>('idle')

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (state !== 'idle') return
    setState('loading')
    // Демонстрационная отправка (без бэкенда).
    setTimeout(() => setState('done'), 1100)
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <AnimatePresence mode="wait">
        {state === 'done' ? (
          <motion.div
            key="done"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center gap-3 rounded-2xl border border-brand/40 bg-brand/5 px-6 py-10 text-center"
          >
            <span className="grid size-12 place-items-center rounded-full bg-brand text-ink">
              <Check className="size-6" />
            </span>
            <p className="font-display text-xl">Заявка отправлена</p>
            <p className="max-w-sm text-sm text-muted">
              Менеджер «Новой» перезвонит вам в ближайшее время и подберёт
              квартиру под ваш запрос.
            </p>
          </motion.div>
        ) : (
          <motion.div
            key="form"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className={compact ? 'grid gap-3' : 'grid gap-4 sm:grid-cols-2'}
          >
            <Field label="Имя" name="name" placeholder="Как к вам обращаться" />
            <Field
              label="Телефон"
              name="phone"
              type="tel"
              placeholder="+7 (___) ___-__-__"
              required
            />
            {!compact && (
              <div className="sm:col-span-2">
                <Field
                  label="Комментарий"
                  name="comment"
                  placeholder="Например: 2-комнатная в «Новой Жизни»"
                />
              </div>
            )}
            <div className={compact ? '' : 'sm:col-span-2'}>
              <Button
                type="submit"
                className="w-full"
              >
                {state === 'loading' ? (
                  <>
                    <Loader2 className="size-4 animate-spin" /> Отправляем…
                  </>
                ) : (
                  'Получить консультацию'
                )}
              </Button>
              <p className="mt-3 text-center text-xs text-faint">
                Нажимая кнопку, вы соглашаетесь с обработкой персональных данных.
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </form>
  )
}

function Field({
  label,
  name,
  type = 'text',
  placeholder,
  required,
}: {
  label: string
  name: string
  type?: string
  placeholder?: string
  required?: boolean
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-faint">
        {label}
      </span>
      <input
        name={name}
        type={type}
        required={required}
        placeholder={placeholder}
        className="w-full rounded-xl border border-line2 bg-base px-4 py-3 text-sm text-fg outline-none transition-colors placeholder:text-faint focus:border-brand"
      />
    </label>
  )
}
