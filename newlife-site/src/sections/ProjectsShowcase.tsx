import { SectionHeading } from '@/components/ui/SectionHeading'
import { ProjectCard } from '@/components/ProjectCard'
import { Reveal, RevealItem } from '@/components/ui/Reveal'
import { projects } from '@/data/site'

export function ProjectsShowcase() {
  return (
    <section id="projects" className="container-x py-24 md:py-28">
      <SectionHeading
        eyebrow="Наши проекты"
        title="Два микрорайона — один уровень комфорта"
        subtitle="Выберите дом для своей семьи в проектах, где продумана каждая деталь — от планировки до двора."
      />
      <Reveal stagger className="mt-12 grid gap-6 lg:grid-cols-2">
        {projects.map((p) => (
          <RevealItem key={p.slug}>
            <ProjectCard project={p} />
          </RevealItem>
        ))}
      </Reveal>
    </section>
  )
}
