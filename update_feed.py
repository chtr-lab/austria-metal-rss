
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from email.utils import formatdate
from datetime import datetime, timezone
from pathlib import Path
import html

QUERIES = [
    '"Deathcore" Konzert Österreich 2027',
    '"Death Metal" Konzert Österreich 2027',
    '"Brutal Death Metal" Österreich 2027',
    '"Slam Death Metal" Österreich 2027',
    '"Nu Metal" Konzert Österreich 2027',
    '"Slaughter to Prevail" Europe tour 2027',
    '"Lorna Shore" Europe tour 2027',
    '"Signs of the Swarm" Europe tour 2027',
    '"Mental Cruelty" Europe tour 2027',
    '"Carnifex" Europe tour 2027',
    '"Dying Fetus" Europe tour 2027',
    '"Cannibal Corpse" Europe tour 2027',
    '"Whitechapel" Europe tour 2027',
    '"Vended" Europe tour 2027',
]

ATOM = "{http://www.w3.org/2005/Atom}"

items = {}

for query in QUERIES:
    url = (
        "https://news.google.com/rss/search?q="
        + urllib.parse.quote(query)
        + "&hl=de&gl=AT&ceid=AT:de"
    )

    try:
        request = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            root = ET.fromstring(response.read())

        for entry in root.findall(ATOM + "entry"):
            title = entry.findtext(ATOM + "title", "")
            link_element = entry.find(ATOM + "link")
            link = link_element.get("href", "") if link_element is not None else ""
            published = entry.findtext(ATOM + "published", "")
            summary = entry.findtext(ATOM + "summary", "")

            if not title or not link:
                continue

            if link not in items:
                items[link] = {
                    "title": title,
                    "link": link,
                    "date": published,
                    "summary": summary,
                }

    except Exception as error:
        print("Quelle konnte nicht geladen werden:", error)

rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")

ET.SubElement(channel, "title").text = "Austria Metal Concert Radar"
ET.SubElement(channel, "link").text = "https://github.com/"
ET.SubElement(channel, "description").text = (
    "Deathcore, Death Metal, Slam und Nu Metal "
    "Konzertankündigungen für Österreich."
)
ET.SubElement(channel, "language").text = "de-at"
ET.SubElement(channel, "lastBuildDate").text = formatdate(
    datetime.now(timezone.utc).timestamp(), usegmt=True
)

for data in sorted(
    items.values(), key=lambda x: x["date"], reverse=True
):
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = data["title"]
    ET.SubElement(item, "link").text = data["link"]
    ET.SubElement(item, "guid").text = data["link"]
    ET.SubElement(item, "description").text = data["summary"]

    if data["date"]:
        try:
            date = datetime.fromisoformat(
                data["date"].replace("Z", "+00:00")
            )
            ET.SubElement(item, "pubDate").text = formatdate(
                date.timestamp(), usegmt=True
            )
        except ValueError:
            pass

ET.indent(rss, space="  ")

Path("feed.xml").write_bytes(
    ET.tostring(rss, encoding="utf-8", xml_declaration=True)
)

print("RSS-Feed erfolgreich erstellt!")
print("Gefundene Meldungen:", len(items))
