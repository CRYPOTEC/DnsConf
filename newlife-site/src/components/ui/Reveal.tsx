import { motion, type Variants } from 'framer-motion'
import type { ElementType, ReactNode } from 'react'
import { EASE } from '@/lib/motion'

type Direction = 'up' | 'down' | 'left' | 'right' | 'none'

const offset: Record<Direction, { x?: number; y?: number }> = {
  up: { y: 28 },
  down: { y: -28 },
  left: { x: 28 },
  right: { x: -28 },
  none: {},
}

type RevealProps = {
  children: ReactNode
  className?: string
  delay?: number
  direction?: Direction
  /** Если true — анимирует детей по очереди (используется с RevealItem). */
  stagger?: boolean
  as?: 'div' | 'section' | 'ul' | 'li' | 'span'
}

/** Появление контента при попадании в зону видимости. */
export function Reveal({
  children,
  className,
  delay = 0,
  direction = 'up',
  stagger = false,
  as = 'div',
}: RevealProps) {
  const MotionTag = motion[as] as ElementType
  const variants: Variants = stagger
    ? {
        hidden: {},
        show: { transition: { staggerChildren: 0.08, delayChildren: delay } },
      }
    : {
        hidden: { opacity: 0, ...offset[direction] },
        show: {
          opacity: 1,
          x: 0,
          y: 0,
          transition: { duration: 0.7, ease: EASE, delay },
        },
      }

  return (
    <MotionTag
      className={className}
      variants={variants}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: '-80px' }}
    >
      {children}
    </MotionTag>
  )
}

/** Дочерний элемент для контейнера с stagger. */
export const revealItemVariants: Variants = {
  hidden: { opacity: 0, y: 24 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: EASE },
  },
}

export function RevealItem({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <motion.div className={className} variants={revealItemVariants}>
      {children}
    </motion.div>
  )
}
