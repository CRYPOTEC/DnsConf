import { chromium } from 'playwright'
import { mkdirSync } from 'node:fs'

const OUT = '/home/user/DnsConf/reel_work/shots'
mkdirSync(OUT, { recursive: true })

const routes = [
  ['home', '/'],
  ['newlife', '/newlife'],
  ['naganova', '/naganova'],
  ['apartments', '/apartments'],
  ['mortgage', '/mortgage'],
  ['about', '/about'],
  ['contacts', '/contacts'],
]

async function settle(page) {
  // Прокрутка по странице, чтобы сработали whileInView-анимации (once:true).
  // Идём медленно, чтобы IntersectionObserver успел зарегистрировать каждую секцию.
  await page.evaluate(async () => {
    const h = document.body.scrollHeight
    const vh = window.innerHeight
    for (let y = 0; y <= h; y += Math.round(vh * 0.5)) {
      window.scrollTo(0, y)
      await new Promise((r) => setTimeout(r, 320))
    }
    window.scrollTo(0, h)
    await new Promise((r) => setTimeout(r, 500))
    window.scrollTo(0, 0)
  })
  await page.waitForTimeout(900)
}

const browser = await chromium.launch()

// Desktop
const ctx = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  deviceScaleFactor: 2,
})
const page = await ctx.newPage()
for (const [name, route] of routes) {
  await page.goto('http://localhost:4173' + route, { waitUntil: 'networkidle' })
  await page.waitForTimeout(900) // дать шрифтам/hero-анимации
  await settle(page)
  await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: true })
  console.log('shot', name)
}
await ctx.close()

// Mobile (home + apartments)
const mctx = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 3,
  isMobile: true,
})
const mpage = await mctx.newPage()
for (const [name, route] of [
  ['home', '/'],
  ['mortgage', '/mortgage'],
]) {
  await mpage.goto('http://localhost:4173' + route, { waitUntil: 'networkidle' })
  await mpage.waitForTimeout(900)
  await settle(mpage)
  await mpage.screenshot({ path: `${OUT}/mobile-${name}.png`, fullPage: true })
  console.log('shot mobile', name)
}
await mctx.close()

await browser.close()
console.log('done ->', OUT)
