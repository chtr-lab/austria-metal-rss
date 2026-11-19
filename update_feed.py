
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from email.utils import formatdate, parsedate_to_datetime
from datetime import datetime, timezone
from pathlib import Path

QUERIES = [
    '"Deathcore" Konzert Österreich',
    '"Death Metal" Konzert Österreich',
    '"Brutal Death Metal" Österreich',
    '"Slam Death Metal" Österreich',
    '"Nu Metal" Konzert Österreich',
    '"Slaughter to Prevail" Europe tour',
    '"Lorna Shore" Europe tour',
    '"Signs of the Swarm" Europe tour',
    '"Mental Cruelty" Europe tour',
    '"Carnifex" Europe tour',
    '"Dying Fetus" Europe tour',
    '"Cannibal Corpse" Europe tour',
    '"Whitechapel" Europe tour',
    '"Vended" Europe tour',
    '"200 Stab Wounds" Europe tour',
]

items = {}

for query in QUERIES:
    url = (
        "https://news.google.com/rss/search?q="
        + urllib.parse.quote(query + " -festival")
        + "&hl=de&gl=AT&ceid=AT:de"
    )

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            root = ET.fromstring(response.read())

        for entry in root.findall("./channel/item"):
            title = entry.findtext("title", "")
            link = entry.findtext("link", "")
            date = entry.findtext("pubDate", "")
            description = entry.findtext("description", "")

            if not title or not link:
                continue

            items[link] = {
                "title": title,
                "link": link,
                "date": date,
                "description": description,
            }

        print("Quelle erfolgreich:", query)

    except Exception as error:
        print("Fehler bei:", query, error)

rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")

ET.SubElement(channel, "title").text = (
    "Austria Metal Concert Radar"
)
ET.SubElement(channel, "link").text = (
    "https://github.com/"
)
ET.SubElement(channel, "description").text = (
    "Deathcore, Death Metal, Brutal Death, "
    "Slam und Nu Metal Konzertankündigungen."
)
ET.SubElement(channel, "language").text = "de-at"

ET.SubElement(channel, "lastBuildDate").text = formatdate(
    datetime.now(timezone.utc).timestamp(),
    usegmt=True
)

def sort_date(item):
    try:
        return parsedate_to_datetime(item["date"])
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)

for data in sorted(items.values(), key=sort_date, reverse=True):
    item = ET.SubElement(channel, "item")

    ET.SubElement(item, "title").text = data["title"]
    ET.SubElement(item, "link").text = data["link"]
    ET.SubElement(item, "guid").text = data["link"]
    ET.SubElement(item, "description").text = data["description"]

    if data["date"]:
        ET.SubElement(item, "pubDate").text = data["date"]

ET.indent(rss, space="  ")

Path("feed.xml").write_bytes(
    ET.tostring(
        rss,
        encoding="utf-8",
        xml_declaration=True
    )
)

print("RSS-Feed erstellt!")
print("Gefundene Meldungen:", len(items))
