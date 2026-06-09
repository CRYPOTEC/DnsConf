import { Hero } from '@/sections/Hero'
import { StatsBar } from '@/sections/StatsBar'
import { ProjectsShowcase } from '@/sections/ProjectsShowcase'
import { Promos } from '@/sections/Promos'
import { Advantages } from '@/sections/Advantages'
import { NewsSection } from '@/sections/NewsSection'
import { CTASection } from '@/sections/CTASection'

export function Home() {
  return (
    <>
      <Hero />
      <StatsBar />
      <ProjectsShowcase />
      <Promos />
      <Advantages />
      <NewsSection />
      <CTASection />
    </>
  )
}
