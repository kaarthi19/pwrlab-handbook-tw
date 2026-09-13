"""Build a fully self-contained handbook: no JS, no CDN, renders offline forever."""
import re, os, html, markdown

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, 'NODE_GUIDE.md')
src = open(MD).read()

# Drop the H1 and the Contents block (the sidebar replaces them)
src = src.split('\n', 1)[1]
i = src.index('## Contents'); j = src.index('\n---\n', i)
src = src[j+5:].lstrip()

body = markdown.markdown(src, extensions=['tables', 'fenced_code', 'sane_lists', 'attr_list'])

# Anchor every top-level heading and collect the nav
nav, n = [], 0
def anchor(m):
    global n
    n += 1
    text = m.group(1)
    sid = 'sec-%d' % n
    pm = re.match(r'Part\s+(\d+)\s*[—–-]\s*(.*)$', text)
    num = pm.group(1).zfill(2) if pm else '→'
    label = pm.group(2) if pm else text
    nav.append((sid, num, label, pm is None))
    return '<h1 id="%s">%s</h1>' % (sid, text)
body = re.sub(r'<h1>(.*?)</h1>', anchor, body, flags=re.S)

# Wide content scrolls in its own container
body = body.replace('<table>', '<div class="tw"><table>').replace('</table>', '</table></div>')

# Terminal label on each code block
body = re.sub(r'<pre><code class="language-(\w+)">',
              lambda m: '<pre data-lang="%s"><code>' % ('terminal' if m.group(1)=='bash' else m.group(1)), body)
body = body.replace('<pre><code>', '<pre data-lang="terminal"><code>')

# Severity on blockquotes
DANGER = re.compile(r'permanent|no undo|irreversible|erase the entire', re.I)
WARN   = re.compile(r'not optional|watch out|caution|re-read|be careful|never', re.I)
def bq(m):
    inner = m.group(1)
    txt = re.sub(r'<[^>]+>', '', inner)
    cls = 'danger' if DANGER.search(txt) else ('warn' if WARN.search(txt) else '')
    return '<blockquote%s>%s</blockquote>' % (' class="%s"' % cls if cls else '', inner)
body = re.sub(r'<blockquote>(.*?)</blockquote>', bq, body, flags=re.S)

navhtml = '\n'.join(
    '<li%s><a href="#%s"><span class="n">%s</span><span>%s</span></a></li>'
    % (' class="lead"' if lead else '', sid, num, html.escape(label))
    for sid, num, label, lead in nav)

css = '<style>\n' + open(os.path.join(HERE, 'style.css')).read() + '</style>'

out = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The pwrlab Handbook</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@600;700&family=IBM+Plex+Serif:ital,wght@0,400;0,600;1,400&display=swap">
{css}
<style>body{{margin:0}} img{{max-width:100%}}</style>
</head><body>
<div class="shell">
  <aside class="rail">
    <div class="rail-head">
      <div class="mark">Power&nbsp;Lab &middot; UC San Diego</div>
      <h2 class="rail-title">The pwrlab<br>Handbook</h2>
      <p class="rail-sub">Running the China energy&nbsp;pathways model on a shared Linux node.</p>
    </div>
    <dl class="vitals">
      <div class="vital"><dt>Host</dt><dd>pwrlab</dd></div>
      <div class="vital"><dt>Connect to</dt><dd>pwrlab.ucsd.edu</dd></div>
      <div class="vital"><dt>Account</dt><dd>taw021</dd></div>
      <div class="vital"><dt>Cores</dt><dd>72</dd></div>
      <div class="vital"><dt>Memory</dt><dd>187 GB</dd></div>
      <div class="vital"><dt>OS</dt><dd>Ubuntu 24.04</dd></div>
    </dl>
    <p class="nav-label">Contents</p>
    <div class="nav-wrap"><ul class="nav">{navhtml}</ul></div>
  </aside>
  <main class="main">
    <header class="masthead">
      <div class="mark">Field guide &middot; offline copy</div>
      <h1>Using the node, from zero</h1>
      <p class="lede">Parts 1&ndash;3 get you connected. Parts 4&ndash;5 explain how the model and the machine actually work, so the rest is reasoning rather than recitation. Everything after that is the practical how-to.</p>
      <dl class="strip">
        <div><dt>Processor</dt><dd>Xeon 6240</dd></div>
        <div><dt>Cores</dt><dd>72</dd></div>
        <div><dt>RAM</dt><dd>187 GB</dd></div>
        <div><dt>Parts</dt><dd>17</dd></div>
      </dl>
    </header>
    <article class="doc">{body}</article>
  </main>
</div>
</body></html>'''
open(os.path.join(HERE, 'index.html'), 'w').write(out)
print('wrote %.0f KB, %d nav entries, 0 scripts' % (len(out)/1024, len(nav)))
