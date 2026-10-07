#!/usr/bin/env python3
"""Rewrite the Writing section of README.md with the newest posts from the blog feed."""
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

FEED = "https://tudorturcanu.ch/rss.xml"
README = "README.md"
COUNT = 5
START, END = "<!-- writing:start -->", "<!-- writing:end -->"

request = urllib.request.Request(FEED, headers={"User-Agent": "profile-readme"})
with urllib.request.urlopen(request, timeout=30) as response:
    channel = ET.fromstring(response.read()).find("channel")

posts = []
for item in channel.findall("item")[:COUNT]:
    title = (item.findtext("title") or "").strip()
    link = (item.findtext("link") or "").strip()
    # Only accept links back to the blog, so a broken feed can't inject anything else.
    if title and link.startswith("https://tudorturcanu.ch/"):
        title = re.sub(r"\s+", " ", title).replace("[", "\\[").replace("]", "\\]")
        posts.append(f"- [{title}]({link})")

if not posts:
    sys.exit("No posts found in the feed; leaving README.md untouched.")

readme = open(README, encoding="utf-8").read()
if START not in readme or END not in readme:
    sys.exit("Writing markers are missing from README.md.")

head, rest = readme.split(START, 1)
_, tail = rest.split(END, 1)
updated = f"{head}{START}\n" + "\n".join(posts) + f"\n{END}{tail}"

if updated != readme:
    open(README, "w", encoding="utf-8").write(updated)
    print(f"README.md updated with {len(posts)} posts.")
else:
    print("README.md is already up to date.")
