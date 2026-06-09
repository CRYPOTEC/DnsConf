import { useEffect, useRef } from 'react'
import {
  useInView,
  useMotionValue,
  useSpring,
  useTransform,
  motion,
} from 'framer-motion'

type Props = {
  value: number
  suffix?: string
  /** Кол-во знаков после запятой. */
  decimals?: number
  className?: string
}

/** Счётчик, плавно набирающий значение при появлении. */
export function AnimatedCounter({
  value,
  suffix = '',
  decimals = 0,
  className,
}: Props) {
  const ref = useRef<HTMLSpanElement>(null)
  const inView = useInView(ref, { once: true, margin: '-60px' })
  const mv = useMotionValue(0)
  const spring = useSpring(mv, { duration: 1600, bounce: 0 })
  const text = useTransform(spring, (latest) =>
    latest.toLocaleString('ru-RU', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }),
  )

  useEffect(() => {
    if (inView) mv.set(value)
  }, [inView, value, mv])

  return (
    <span ref={ref} className={className}>
      <motion.span>{text}</motion.span>
      {suffix}
    </span>
  )
}
