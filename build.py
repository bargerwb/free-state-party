#!/usr/bin/env python3
"""
Free State Party — Build Script

Reads content/*.md files + templates/base.html, generates multi-page site.

Output:
  site/index.html  — Home (hero + video)
  site/about.html  — About (pitch + what this is)
  site/events.html — Events
  site/join.html   — Come Meet Us (concierge form)

Usage: python3 build.py
"""

import json
import os
import re
import shutil

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(SCRIPT_DIR, 'content')
TEMPLATE_DIR = os.path.join(SCRIPT_DIR, 'templates')
SITE_DIR = os.path.join(SCRIPT_DIR, 'site')


def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def md_to_html(text):
    """Convert simple markdown paragraphs to HTML. Returns (h2_title, body_html)."""
    lines = text.strip().split('\n')
    h2_title = ''
    body_lines = []
    skip_blank = False

    for line in lines:
        stripped = line.strip()
        # Skip H1
        if stripped.startswith('# ') and not stripped.startswith('## '):
            skip_blank = True
            continue
        # Capture H2 as section title
        if stripped.startswith('## '):
            h2_title = stripped[3:].strip()
            skip_blank = True
            continue
        if skip_blank and stripped == '':
            skip_blank = False
            continue
        skip_blank = False
        body_lines.append(line)

    body_text = '\n'.join(body_lines).strip()
    paragraphs = re.split(r'\n\s*\n', body_text)
    html_parts = []

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        # Skip metadata-only paragraphs (every line matches key: value)
        if all(re.match(r'^[a-z_]+:', line) for line in p.split('\n') if line.strip()):
            continue
        # Bold → <strong>
        p = re.sub(r'\*\*(.+?)\*\*', r'<strong class="text-dark-50">\1</strong>', p)
        # Italic → <em>
        p = re.sub(r'\*(.+?)\*', r'<em>\1</em>', p)
        # Em dashes
        p = p.replace(' — ', ' &mdash; ')
        p = p.replace('— ', '&mdash; ')
        html_parts.append(f'<p>{p}</p>')

    return h2_title, '\n                '.join(html_parts)


def parse_events(text):
    """Parse events.md into open and closed event lists. Returns (open_cards, closed_cards)."""
    lines = text.strip().split('\n')
    section = None  # 'open' or 'closed'
    events = {'open': [], 'closed': []}
    current = {}

    for line in lines:
        stripped = line.strip()
        if stripped.lower() == '## open events':
            section = 'open'
            continue
        elif stripped.lower() == '## closed events':
            if current and section:
                events[section].append(current)
                current = {}
            section = 'closed'
            continue
        elif stripped.startswith('# '):
            continue

        if stripped.startswith('- title:'):
            if current and section:
                events[section].append(current)
            current = {'title': stripped[8:].strip()}
        elif stripped.startswith('date:'):
            current['date'] = stripped[5:].strip()
        elif stripped.startswith('time:'):
            current['time'] = stripped[5:].strip()
        elif stripped.startswith('location:'):
            current['location'] = stripped[9:].strip()
        elif stripped.startswith('description:'):
            current['description'] = stripped[12:].strip()
        elif stripped.startswith('link:'):
            current['link'] = stripped[5:].strip()

    if current and section:
        events[section].append(current)

    def make_link(href):
        """Convert internal absolute links to use {{base}} for relative resolution."""
        if href.startswith('/'):
            return '{{base}}' + href
        return href

    def render_cards(event_list, is_open=False):
        cards = []
        for event in event_list:
            details = []
            if event.get('time'):
                details.append(event['time'])
            if event.get('location'):
                details.append(event['location'])
            details_html = ''
            if details:
                details_html = f'<p class="text-dark-400 text-sm mb-2">{" &bull; ".join(details)}</p>'

            link = make_link(event['link']) if event.get('link') else ''
            link_html = ''
            if link:
                link_html = f'<a href="{link}" class="inline-block mt-3 text-gold-500 hover:text-gold-400 text-sm font-medium transition-colors">Learn more &rarr;</a>'

            title_html = event.get('title', '')
            if link:
                title_html = f'<a href="{link}" class="hover:text-gold-500 transition-colors">{title_html}</a>'

            card = f'''<div class="bg-dark-900 border border-dark-600 rounded-lg p-6 hover:border-gold-700/50 transition-colors">
                    <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 mb-3">
                        <h3 class="font-display text-xl font-bold text-dark-50">{title_html}</h3>
                        <span class="text-gold-500 font-medium text-sm whitespace-nowrap">{event.get("date", "")}</span>
                    </div>
                    {details_html}
                    <p class="text-dark-300 leading-relaxed">{event.get("description", "")}</p>
                    {link_html}
                </div>'''
            cards.append(card)
        return '\n                '.join(cards)

    return render_cards(events['open'], is_open=True), render_cards(events['closed'])


def parse_words(text):
    return [w.strip() for w in text.strip().split('\n') if w.strip()]


def build_page(base, page_title, page_description, og_title, page_content,
               page_scripts='', active_nav=None, is_subdir=False, base_path=None):
    """Inject content into base template and return final HTML."""
    html = base
    html = html.replace('{{page_title}}', page_title)
    html = html.replace('{{page_description}}', page_description)
    html = html.replace('{{og_title}}', og_title)
    html = html.replace('{{page_content}}', page_content)
    html = html.replace('{{page_scripts}}', page_scripts)

    # Relative base path: explicit base_path overrides is_subdir
    if base_path is not None:
        resolved_base = base_path
    else:
        resolved_base = '..' if is_subdir else '.'
    html = html.replace('{{base}}', resolved_base)

    # Nav active states
    for nav in ['about', 'events']:
        cls = 'nav-active' if active_nav == nav else 'text-dark-200'
        html = html.replace(f'{{{{nav_{nav}_class}}}}', cls)

    return html


def build():
    print("Building Free State Party site...")

    base = read_file(os.path.join(TEMPLATE_DIR, 'base.html'))

    # --- Read content ---
    hero_text = read_file(os.path.join(CONTENT_DIR, 'hero.md'))
    hero = {}
    for line in hero_text.split('\n'):
        if ':' in line and not line.startswith('#'):
            key, val = line.split(':', 1)
            hero[key.strip()] = val.strip()

    words = parse_words(read_file(os.path.join(CONTENT_DIR, 'words.md')))

    pitch_text = read_file(os.path.join(CONTENT_DIR, 'pitch.md'))
    pitch_title, pitch_body = md_to_html(pitch_text)

    what_text = read_file(os.path.join(CONTENT_DIR, 'what-this-is.md'))
    what_title, what_body = md_to_html(what_text)

    events_text = read_file(os.path.join(CONTENT_DIR, 'events.md'))
    open_events_html, closed_events_html = parse_events(events_text)


    # --- Page 1: Home (hero + video) ---
    home_content = f'''
    <section class="min-h-screen flex flex-col justify-center px-6 pt-20 pb-12 md:py-0">
        <div class="max-w-6xl mx-auto w-full lg:grid lg:grid-cols-2 lg:gap-12 lg:items-center">
            <div>
                <h1 class="font-display text-4xl sm:text-5xl md:text-6xl lg:text-5xl xl:text-6xl font-bold leading-tight mb-6">
                    <span class="text-dark-50">A private club for</span><br>
                    <span class="gold-gradient cycle-word" id="cycling-word" aria-live="polite">{words[0]}</span><br>
                    <span class="text-dark-50">free staters.</span>
                </h1>
                <p class="text-xl sm:text-2xl lg:text-xl xl:text-2xl text-dark-200 leading-relaxed max-w-2xl mb-10 font-display italic">
                    {hero.get('sub_tagline', 'We have a plan.')}
                </p>
                <a href="{{{{base}}}}/saturday/" class="inline-block bg-gold-500 hover:bg-gold-400 text-dark-900 font-bold text-lg px-10 py-4 rounded-lg transition-colors min-h-[48px]">
                    Meet Us
                </a>
            </div>
            <div class="mt-12 lg:mt-0">
                <div class="video-container shadow-2xl" id="video-wrapper">
                    <video id="hero-video" preload="metadata" playsinline>
                        <source src="{{{{base}}}}/video/homepage.mp4" type="video/mp4">
                    </video>
                    <button id="video-play" class="video-overlay" aria-label="Play video">
                        <svg width="72" height="72" viewBox="0 0 72 72" fill="none">
                            <circle cx="36" cy="36" r="35" stroke="#d4a017" stroke-width="2" fill="rgba(10,10,10,0.6)"/>
                            <polygon points="28,20 28,52 54,36" fill="#d4a017"/>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </section>'''

    home_scripts = f'''<script>
        const words = {json.dumps(words)};
        const el = document.getElementById('cycling-word');
        let currentIndex = 0;
        let paused = false;

        function cycleWord() {{
            if (paused) return;
            el.classList.add('fade-out');
            setTimeout(() => {{
                currentIndex = (currentIndex + 1) % words.length;
                el.textContent = words[currentIndex];
                el.classList.remove('fade-out');
            }}, 300);
        }}

        setInterval(cycleWord, 2500);

        document.addEventListener('visibilitychange', () => {{
            paused = document.hidden;
        }});

        // Video player
        const video = document.getElementById('hero-video');
        const playBtn = document.getElementById('video-play');
        if (video && playBtn) {{
            playBtn.addEventListener('click', () => {{
                playBtn.style.display = 'none';
                video.controls = true;
                video.play();
            }});
            video.addEventListener('ended', () => {{
                playBtn.style.display = 'flex';
                video.controls = false;
            }});
        }}
    </script>'''

    home_html = build_page(
        base,
        page_title='Free State Party — A Private Club for Free Staters',
        page_description='A private club for liberty-minded free staters in New Hampshire. We didn\'t come here to attend committee meetings. We came here to build something.',
        og_title='Free State Party',
        page_content=home_content,
        page_scripts=home_scripts,
        active_nav=None
    )

    # --- Page 2: About (pitch + what this is) ---
    about_content = f'''
    <section class="px-6 pt-32 pb-20 md:pt-40 md:pb-28 bg-dark-800">
        <div class="max-w-3xl mx-auto">
            <div class="divider mb-6"></div>
            <h2 class="font-display text-3xl md:text-4xl font-bold text-dark-50 mb-10">{pitch_title}</h2>
            <div class="space-y-6 text-lg text-dark-200 leading-relaxed">
                {pitch_body}
            </div>
        </div>
    </section>

    <section class="px-6 py-20 md:py-28">
        <div class="max-w-3xl mx-auto">
            <div class="divider mb-6"></div>
            <h2 class="font-display text-3xl md:text-4xl font-bold text-dark-50 mb-10">{what_title}</h2>
            <div class="space-y-6 text-lg text-dark-200 leading-relaxed">
                {what_body}
            </div>
        </div>
    </section>

    <section class="px-6 pb-20 md:pb-28 text-center">
        <a href="{{{{base}}}}/saturday/" class="inline-block bg-gold-500 hover:bg-gold-400 text-dark-900 font-bold text-lg px-10 py-4 rounded-lg transition-colors min-h-[48px]">
            Come Meet Us
        </a>
    </section>'''

    about_html = build_page(
        base,
        page_title='About — Free State Party',
        page_description='Not a nonprofit. Not a political party. A private club for liberty-minded free staters in New Hampshire.',
        og_title='About — Free State Party',
        page_content=about_content,
        active_nav='about',
        is_subdir=True
    )

    # --- Page 3: Events (tabbed: open / closed) ---
    events_content = f'''
    <section class="px-6 pt-32 pb-20 md:pt-40 md:pb-28">
        <div class="max-w-3xl mx-auto">
            <div class="divider mb-6"></div>
            <h2 class="font-display text-3xl md:text-4xl font-bold text-dark-50 mb-8">Events</h2>

            <!-- Tabs -->
            <div class="flex gap-2 mb-10">
                <button id="tab-open" class="events-tab px-5 py-2.5 rounded-lg font-medium text-sm transition-colors bg-gold-500 text-dark-900" data-tab="open">
                    Open
                </button>
                <button id="tab-closed" class="events-tab px-5 py-2.5 rounded-lg font-medium text-sm transition-colors bg-dark-800 text-dark-300 hover:text-dark-100" data-tab="closed">
                    Members Only
                </button>
            </div>

            <!-- Open Events -->
            <div id="events-open" class="events-panel grid gap-6">
                {open_events_html}
            </div>

            <!-- Closed Events -->
            <div id="events-closed" class="events-panel hidden">
                <p class="text-2xl text-dark-200 font-display italic">Private.</p>
            </div>
        </div>
    </section>'''

    events_scripts = '''<script>
        document.querySelectorAll('.events-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.dataset.tab;

                // Toggle panels
                document.querySelectorAll('.events-panel').forEach(p => p.classList.add('hidden'));
                document.getElementById('events-' + target).classList.remove('hidden');

                // Toggle tab styles
                document.querySelectorAll('.events-tab').forEach(t => {
                    t.className = 'events-tab px-5 py-2.5 rounded-lg font-medium text-sm transition-colors bg-dark-800 text-dark-300 hover:text-dark-100';
                });
                tab.className = 'events-tab px-5 py-2.5 rounded-lg font-medium text-sm transition-colors bg-gold-500 text-dark-900';
            });
        });
    </script>'''

    events_html_page = build_page(
        base,
        page_title='Events — Free State Party',
        page_description='Open and members-only events from the Free State Party in New Hampshire.',
        og_title='Events — Free State Party',
        page_content=events_content,
        page_scripts=events_scripts,
        active_nav='events',
        is_subdir=True
    )


    # --- Page 5: Saturdays (unlisted landing page) ---
    saturdays_text = read_file(os.path.join(CONTENT_DIR, 'saturdays.md'))
    saturdays_meta = {}
    for line in saturdays_text.split('\n'):
        if ':' in line and not line.startswith('#'):
            key, val = line.split(':', 1)
            if key.strip().isidentifier():
                saturdays_meta[key.strip()] = val.strip()
    saturdays_title, saturdays_body = md_to_html(saturdays_text)

    sat_address = saturdays_meta.get('address', '')
    sat_maps_url = 'https://www.google.com/maps/search/' + sat_address.replace(' ', '+') if sat_address else ''
    sat_event_id = saturdays_meta.get('event_id', '')

    saturdays_content = f'''
    <section class="px-6 pt-32 pb-12 md:pt-40 md:pb-16">
        <div class="max-w-4xl mx-auto text-center">
            <div class="divider mb-6 mx-auto"></div>
            <h1 class="font-display text-4xl md:text-5xl lg:text-6xl font-bold text-dark-50 mb-6">{saturdays_title if saturdays_title else "Free State Saturdays"}</h1>
            <div class="space-y-4 text-lg text-dark-200 leading-relaxed max-w-2xl mx-auto">
                {saturdays_body}
            </div>
        </div>
    </section>

    <section class="px-6 pb-8 md:pb-10 text-center">
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="./rsvp/" class="inline-flex items-center justify-center bg-gold-500 hover:bg-gold-400 text-dark-900 font-bold text-lg px-10 py-4 rounded-lg transition-colors min-h-[48px]">
                RSVP
            </a>
            <a href="{sat_maps_url}" target="_blank" rel="noopener" class="inline-flex items-center justify-center gap-2 bg-dark-700 hover:bg-dark-600 text-dark-100 font-bold text-lg px-10 py-4 rounded-lg transition-colors min-h-[48px]">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                Map
            </a>
        </div>
    </section>

    <section class="px-6 pb-8 md:pb-10">
        <div class="max-w-4xl mx-auto">
            <a href="{sat_maps_url}" target="_blank" rel="noopener" class="block select-none">
                <img src="{{{{base}}}}/img/saturdays-poster.jpg" alt="Free State Saturdays — this month's gathering"
                     class="w-full rounded-lg shadow-2xl hover:opacity-90 transition-opacity" style="max-height: min(80vh, 2000px); object-fit: contain;">
            </a>
        </div>
    </section>

    <section class="px-6 pb-20 md:pb-28 text-center">
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="./rsvp/" class="inline-flex items-center justify-center bg-gold-500 hover:bg-gold-400 text-dark-900 font-bold text-lg px-10 py-4 rounded-lg transition-colors min-h-[48px]">
                RSVP
            </a>
            <a href="{sat_maps_url}" target="_blank" rel="noopener" class="inline-flex items-center justify-center gap-2 bg-dark-700 hover:bg-dark-600 text-dark-100 font-bold text-lg px-10 py-4 rounded-lg transition-colors min-h-[48px]">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                Map
            </a>
        </div>
    </section>'''

    saturdays_html = build_page(
        base,
        page_title='Free State Saturdays — Free State Party',
        page_description='A monthly open gathering for liberty-minded people in New Hampshire. No membership required.',
        og_title='Free State Saturdays',
        page_content=saturdays_content,
        active_nav=None,
        is_subdir=True
    )

    # --- Page 6: RSVP (standalone form at /saturday/rsvp/) ---
    rsvp_content = f'''
    <section class="min-h-screen flex flex-col items-center justify-center px-6 py-24">
        <div class="max-w-md w-full">

            <!-- Form -->
            <div id="rsvp-form-wrap">
                <div class="divider mb-6"></div>
                <h1 class="font-display text-3xl md:text-4xl font-bold text-dark-50 mb-2">RSVP</h1>
                <p class="text-dark-300 mb-8">We&rsquo;ll see you Saturday.</p>
                <form id="rsvp-form" class="space-y-5" novalidate>
                    <input type="hidden" name="event_id" value="{sat_event_id}">
                    <div>
                        <label class="block text-sm font-medium text-dark-200 mb-1.5" for="rsvp-name">Name</label>
                        <input id="rsvp-name" name="name" type="text" required autocomplete="name"
                               class="form-input w-full bg-dark-800 border border-dark-600 text-dark-50 placeholder-dark-500 rounded-lg px-4 py-3"
                               placeholder="Your name">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-dark-200 mb-1.5" for="rsvp-email">Email</label>
                        <input id="rsvp-email" name="email" type="email" required autocomplete="email"
                               class="form-input w-full bg-dark-800 border border-dark-600 text-dark-50 placeholder-dark-500 rounded-lg px-4 py-3"
                               placeholder="you@example.com">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-dark-200 mb-1.5" for="rsvp-guests">
                            Guests <span class="text-dark-500 font-normal">(optional)</span>
                        </label>
                        <select id="rsvp-guests" name="guests"
                                class="form-input w-full bg-dark-800 border border-dark-600 text-dark-50 rounded-lg px-4 py-3">
                            <option value="">Just me</option>
                            <option value="1">+1</option>
                            <option value="2">+2</option>
                            <option value="3">+3</option>
                            <option value="4">+4</option>
                            <option value="5">+5</option>
                        </select>
                    </div>
                    <p id="rsvp-error" class="hidden text-red-400 text-sm"></p>
                    <button type="submit" id="rsvp-submit"
                            class="w-full bg-gold-500 hover:bg-gold-400 text-dark-900 font-bold text-lg py-4 rounded-lg transition-colors min-h-[48px]">
                        Submit RSVP
                    </button>
                </form>
            </div>

            <!-- Success state -->
            <div id="rsvp-success" class="hidden text-center py-8">
                <svg class="mx-auto mb-6" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#d4a017" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="9 12 11 14 15 10"/>
                </svg>
                <h2 class="font-display text-3xl font-bold text-dark-50 mb-3">You&rsquo;re on the list.</h2>
                <p class="text-dark-300">We&rsquo;ll see you Saturday.</p>
            </div>

        </div>
    </section>'''

    rsvp_scripts = '''<script>
        const RSVP_ENDPOINT = window.location.hostname === 'localhost'
            ? 'http://localhost:3000/api/rsvp'
            : 'https://app.freestate.party/api/rsvp';

        document.getElementById('rsvp-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = document.getElementById('rsvp-submit');
            const errorEl = document.getElementById('rsvp-error');

            const name = document.getElementById('rsvp-name').value.trim();
            const email = document.getElementById('rsvp-email').value.trim();
            const guestsVal = document.getElementById('rsvp-guests').value;
            const guests = guestsVal !== '' ? parseInt(guestsVal, 10) : null;
            const eventId = document.querySelector('input[name="event_id"]').value || null;

            if (!name || !email) {
                errorEl.textContent = 'Name and email are required.';
                errorEl.classList.remove('hidden');
                return;
            }

            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting\u2026';
            errorEl.classList.add('hidden');

            try {
                const resp = await fetch(RSVP_ENDPOINT, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, guests, event_id: eventId }),
                });

                if (!resp.ok) {
                    const data = await resp.json().catch(() => ({}));
                    throw new Error(data.message || 'Something went wrong. Please try again.');
                }

                document.getElementById('rsvp-form-wrap').classList.add('hidden');
                document.getElementById('rsvp-success').classList.remove('hidden');
            } catch (err) {
                errorEl.textContent = err.message;
                errorEl.classList.remove('hidden');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit RSVP';
            }
        });
    </script>'''

    rsvp_html = build_page(
        base,
        page_title='RSVP — Free State Saturdays',
        page_description='RSVP for Free State Saturday, a monthly open gathering in New Hampshire.',
        og_title='RSVP — Free State Saturdays',
        page_content=rsvp_content,
        page_scripts=rsvp_scripts,
        active_nav=None,
        base_path='../..'
    )

    # --- Write all pages ---
    # Root page stays as index.html; all others become <name>/index.html for clean URLs
    pages = {
        'index.html': home_html,
        'about/index.html': about_html,
        'events/index.html': events_html_page,
        'saturday/index.html': saturdays_html,
        'saturday/rsvp/index.html': rsvp_html,
    }

    for filepath, html in pages.items():
        full_path = os.path.join(SITE_DIR, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  Built: site/{filepath}")

    # --- Copy video if not already present ---
    video_src = os.path.expanduser('~/Desktop/free-state-party-homepage-video.mp4')
    video_dst = os.path.join(SITE_DIR, 'video', 'homepage.mp4')
    if os.path.exists(video_src) and not os.path.exists(video_dst):
        os.makedirs(os.path.join(SITE_DIR, 'video'), exist_ok=True)
        shutil.copy2(video_src, video_dst)
        print("  Copied: video/homepage.mp4")

    print(f"\nDone. {len(pages)} pages built.")
    print(f"Words: {words}")


def watch():
    """Watch content/ and templates/ for changes, rebuild automatically."""
    import time

    watch_dirs = [CONTENT_DIR, TEMPLATE_DIR]

    def get_mtimes():
        mtimes = {}
        for d in watch_dirs:
            for root, _, files in os.walk(d):
                for f in files:
                    path = os.path.join(root, f)
                    mtimes[path] = os.path.getmtime(path)
        return mtimes

    print("Watching for changes... (Ctrl+C to stop)\n")
    build()
    last = get_mtimes()

    try:
        while True:
            time.sleep(0.5)
            current = get_mtimes()
            if current != last:
                changed = [p for p in current if current.get(p) != last.get(p)]
                for p in changed:
                    print(f"  Changed: {os.path.relpath(p, SCRIPT_DIR)}")
                print()
                build()
                print()
                last = current
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == '__main__':
    import sys
    if '--watch' in sys.argv or '-w' in sys.argv:
        watch()
    else:
        build()
