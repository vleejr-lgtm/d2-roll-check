# Pinned Activity panel at many widths: no header/toolbar control behind the panel or off screen,
# no button text wrapping inside its button, panel close button visible.
import asyncio
from playwright.async_api import async_playwright
CHECK = """(() => {
  const W = innerWidth, pin = parseInt(getComputedStyle(document.body).getPropertyValue('--pinw')) || 0, limit = W - pin + 1;
  const vis = e => e.offsetParent && getComputedStyle(e).visibility !== 'hidden';
  const ctr = [...document.querySelectorAll('header button, header a, header select, .toolbar button, .toolbar select, .toolbar input, .toolbar .chip')].filter(vis);
  const behind = ctr.filter(e => !e.closest('.tabs') && e.getBoundingClientRect().right > limit).map(e => (e.id || e.textContent.trim()).slice(0, 20));
  const wrapped = [...document.querySelectorAll('header button, .toolbar button, .toolbar .chip')].filter(vis).filter(e => { const cs = getComputedStyle(e); return e.getBoundingClientRect().height > parseFloat(cs.lineHeight || 18) * 1.9 + parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom) + 4; }).map(e => (e.id || e.textContent.trim()).slice(0, 20));
  const x = document.getElementById('streamClose').getBoundingClientRect();
  const docW = document.documentElement.scrollWidth;
  return { pin, behind, wrapped, closeVisible: x.right <= W && x.left >= 0, hscroll: docW > W + 1 };
})()"""
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch()
    bad = 0
    for page in ['index.html#weapons', 'armor.html', 'vault.html', 'character.html', 'vendors.html', 'today.html', 'shaders.html']:
      for w in [1920, 1600, 1440, 1280, 1024, 800, 390]:
        pg = await b.new_page(viewport={'width': w, 'height': 800})
        await pg.route('**/*', lambda rt: rt.abort() if 'bungie' in rt.request.url or 'githubusercontent' in rt.request.url else rt.continue_())
        await pg.goto('file:///home/claude/godroll-checker/' + page)
        await pg.evaluate("localStorage.setItem('auth', JSON.stringify({token:'T',exp:Date.now()+3600e3})); localStorage.setItem('streamPinned','1')"); await pg.reload(); await pg.wait_for_timeout(400)
        await pg.evaluate("document.getElementById('stream').classList.remove('hidden'); document.body.classList.add('streampinned'); const b=document.getElementById('btnPM'); if(b) b.classList.remove('hidden'); const c=document.getElementById('charSel'); c.classList.remove('hidden'); c.innerHTML='<option>Pull to: Auto (Warlock, last played)</option>'; const t=document.querySelector('.toolbar'); if(t) t.classList.remove('hidden'); document.querySelectorAll('.toolbar .chips').forEach(x=>x.innerHTML='<span class=chip>God roll<b>398</b></span><span class=chip>Close<b>214</b></span><span class=chip>Trash<b>1</b></span><span class=chip>Unrated<b>7</b></span><span class=chip>Exotic<b>114</b></span>')")
        await pg.wait_for_timeout(200)
        r = await pg.evaluate(CHECK)
        ok = not r['behind'] and not r['wrapped'] and r['closeVisible']
        if not ok: bad += 1
        print(('OK  ' if ok else 'BAD ') + page.ljust(18), w, r)
        if page == 'index.html#weapons' and w in (1440, 1024): await pg.screenshot(path='/home/claude/tests/pin_%d.png' % w)
        await pg.close()
    print('errors', [] if not bad else ['%d layouts bad' % bad])
    await b.close()
asyncio.run(main())
