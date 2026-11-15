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
data = json.loads((HERE / "queue.json").read_text(encoding="utf-8"))
site = data["site"]
today = datetime.now(timezone.utc).date().isoformat()

released = [i for i in data["items"] if i["release"] <= today]
released.sort(key=lambda i: i["release"], reverse=True)
released = released[:50]  # newest 50 is plenty; Pinterest only picks up new items


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


now = format_datetime(datetime.now(timezone.utc))
xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>Office Sorted</title>
  <link>{escape(site)}</link>
  <description>Excel templates, AI prompts and IT tips for small business office admin.</description>
  <language>en-gb</language>
  <lastBuildDate>{now}</lastBuildDate>
  <atom:link href="{escape(site)}feed.xml" rel="self" type="application/rss+xml"/>
{os.linesep.join(item_xml(i) for i in released)}
</channel>
</rss>
"""
(SITE_DIR / "feed.xml").write_text(xml, encoding="utf-8")
print(f"feed.xml: {len(released)} items released (as of {today}); {len(data['items']) - len(released)} still queued")
