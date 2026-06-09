import { Hero } from '@/sections/Hero'
import { StatsBar } from '@/sections/StatsBar'
import { ProjectsShowcase } from '@/sections/ProjectsShowcase'
import { Gallery } from '@/sections/Gallery'
import { Promos } from '@/sections/Promos'
import { Advantages } from '@/sections/Advantages'
import { MicrodistrictBand } from '@/sections/MicrodistrictBand'
import { NewsSection } from '@/sections/NewsSection'
import { CTASection } from '@/sections/CTASection'

export function Home() {
  return (
    <>
      <Hero />
      <StatsBar />
      <ProjectsShowcase />
      <Gallery />
      <Promos />
      <Advantages />
      <MicrodistrictBand />
      <NewsSection />
      <CTASection />
    </>
  )
}
