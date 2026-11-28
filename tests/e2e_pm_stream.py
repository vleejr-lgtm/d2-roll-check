import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(viewport={'width':1600,'height':900}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.route('**/*', lambda rt: rt.abort() if 'bungie' in rt.request.url else rt.continue_())
    await pg.goto('file:///home/claude/godroll-checker/vault.html'); await pg.wait_for_timeout(500)
    vis = lambda sel: pg.evaluate("s => !document.querySelector(s).classList.contains('hidden')", sel)
    await pg.evaluate("document.getElementById('btnPM').classList.remove('hidden')")
    await pg.click('#btnStream'); print('unpinned: stream open', await vis('#stream'))
    await pg.evaluate("document.getElementById('btnPM').click()"); print('  pm open', await vis('#pmPanel'), 'stream steps aside', not await vis('#stream'))
    await pg.click('#pmClose'); print('  pm closed -> stream back', await vis('#stream'))
    await pg.click('#streamPin'); await pg.wait_for_timeout(100)
    await pg.evaluate("document.getElementById('btnPM').click()"); print('pinned: pm open', await vis('#pmPanel'), 'stream stays', await vis('#stream'))
    print('  pm right edge', await pg.evaluate("Math.round(document.getElementById('pmPanel').getBoundingClientRect().right)"), 'stream left', await pg.evaluate("Math.round(document.getElementById('stream').getBoundingClientRect().left)"))
    await pg.evaluate("document.getElementById('btnPM').click()"); print('  pm closed, stream still', await vis('#stream'))
    print('errors', errs); await b.close()
asyncio.run(main())
