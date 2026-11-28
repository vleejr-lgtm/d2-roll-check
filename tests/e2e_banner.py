import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1300,'height':500})
    await pg.route('**/*', lambda rt: rt.abort() if 'bungie.net' in rt.request.url else rt.continue_())
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    for page in ['armor.html','index.html']:
      await pg.goto('file:///home/claude/godroll-checker/'+page)
      await pg.evaluate("localStorage.setItem('auth', JSON.stringify({token:'T',exp:Date.now()-1000}))"); await pg.reload(); await pg.wait_for_timeout(300)
      print(page,'expired:', await pg.is_visible('#authBanner'), '|', await pg.inner_text('#authBanner'))
      if page=='armor.html': await pg.screenshot(path='banner.png')
      await pg.evaluate("localStorage.setItem('auth', JSON.stringify({token:'T',exp:Date.now()+180e3}))"); await pg.reload(); await pg.wait_for_timeout(300)
      print(page,'soon:', await pg.inner_text('#authBanner'))
      await pg.evaluate("localStorage.setItem('auth', JSON.stringify({token:'T',exp:Date.now()+3000e3}))"); await pg.reload(); await pg.wait_for_timeout(300)
      print(page,'fresh hidden:', await pg.is_hidden('#authBanner'))
    print('errors', errs); await b.close()
asyncio.run(main())
