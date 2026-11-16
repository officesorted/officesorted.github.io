"""Releases queued pins into feed.xml (RSS 2.0) for Pinterest auto-publish.
Runs daily in GitHub Actions. Standard library only.
"""
import json
import os
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
SITE_DIR = HERE.parent
FEEDS = [  # (queue file, output file, channel title, channel description)
    ("queue.json", "feed.xml", "Office Sorted", "Excel templates, AI prompts and IT tips for small business office admin."),
    ("queue-home.json", "feed-home.xml", "Home Sorted", "UK household budget, debt and savings tips and spreadsheets."),
    ("queue-se.json", "feed-se.xml", "Self-Employed Sorted", "UK sole trader and side hustle tax, expenses and invoicing tips."),
    ("queue-books.json", "feed-books.xml", "Dino Noodle", "Dinosaur colouring pages and activity books for ages 3-6."),
    ("queue-wedding.json", "feed-wedding.xml", "Home Sorted Wedding Planning", "UK wedding budget and planning tips."),
    ("queue-challenges.json", "feed-challenges.xml", "Home Sorted Savings Challenges", "UK money saving challenges and printables for 2027."),
]
today = datetime.now(timezone.utc).date().isoformat()


def item_xml(i):
    when = datetime.fromisoformat(i["release"]).replace(hour=6, tzinfo=timezone.utc)
    img = escape(i["image"])
    return f"""  <item>
    <title>{escape(i["title"])}</title>
    <link>{escape(i["link"])}</link>
    <guid isPermaLink="false">{escape(i["id"])}</guid>
    <pubDate>{format_datetime(when)}</pubDate>
    <description>{escape(i["description"])}</description>
    <enclosure url="{img}" type="image/png" length="0"/>
    <media:content url="{img}" medium="image" type="image/png"/>
  </item>"""


for qfile, out, ch_title, ch_desc in FEEDS:
    qpath = HERE / qfile
    if not qpath.exists():
        continue
    data = json.loads(qpath.read_text(encoding="utf-8"))
    site = data["site"]
    released = [i for i in data["items"] if i["release"] <= today]
    released.sort(key=lambda i: i["release"], reverse=True)
    released = released[:50]  # newest 50 is plenty; Pinterest only picks up new items
    now = format_datetime(datetime.now(timezone.utc))
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{escape(ch_title)}</title>
  <link>{escape(site)}</link>
  <description>{escape(ch_desc)}</description>
  <language>en-gb</language>
  <lastBuildDate>{now}</lastBuildDate>
  <atom:link href="https://officesorted.github.io/{out}" rel="self" type="application/rss+xml"/>
{os.linesep.join(item_xml(i) for i in released)}
</channel>
</rss>
"""
    (SITE_DIR / out).write_text(xml, encoding="utf-8")
    print(f"{out}: {len(released)} items released (as of {today}); {len(data['items']) - len(released)} still queued")
