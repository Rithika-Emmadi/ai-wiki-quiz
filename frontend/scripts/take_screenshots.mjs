import { chromium } from 'playwright'

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5173/'
const OUT_DIR = process.env.SCREENSHOT_DIR || '../screenshots'

async function main() {
  const browser = await chromium.launch()
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })

  // Tab 1: Quiz generation page
  await page.goto(FRONTEND_URL, { waitUntil: 'domcontentloaded' })
  await page.locator('#url').waitFor({ timeout: 60000 })
  await page.waitForTimeout(250)
  await page.screenshot({ path: `${OUT_DIR}/tab1_generate_quiz.png`, fullPage: true })

  // Generate a quiz to ensure history has a recent entry
  const urlInput = page.locator('#url')
  await urlInput.fill('https://en.wikipedia.org/wiki/Quantum_computing')
  await page.locator('form.generate-form button[type="submit"]').click()
  // Wait for result to appear
  await page.locator('.quiz-display, .quiz-result').first().waitFor({ timeout: 180000 })

  // Tab 2: History view
  await page.locator('header .tabs button', { hasText: 'Past Quizzes' }).click()
  await page.locator('.quizzes-table').waitFor({ timeout: 60000 })
  await page.waitForTimeout(500)
  await page.screenshot({ path: `${OUT_DIR}/tab2_history.png`, fullPage: true })

  // Details modal
  await page.locator('.quizzes-table tbody tr .btn-details').first().click()
  await page.locator('.modal').waitFor({ timeout: 60000 })
  await page.waitForTimeout(500)
  await page.screenshot({ path: `${OUT_DIR}/details_modal.png`, fullPage: true })

  await browser.close()
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})


