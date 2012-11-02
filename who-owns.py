import urllib2
import urllib
import json
import re

def makeWikipediaRequest(title):
  data = {
    "format" : "json",
    "action" : "query",
    "prop"   : "revisions",
    "rvprop" : "content",
    "titles" : title
  }

  data = dict([k.encode('utf-8'), v.encode('utf-8')] for k,v in data.items())
  url =  "http://en.wikipedia.org/w/api.php?%s" % urllib.urlencode(data)

  text = json.loads(urllib2.urlopen(url).read())

  pages = text["query"]["pages"]
  page = pages.values()[0]
  revisions = page["revisions"]
  data = revisions[0]
  text = data["*"]

  return text

def parseWikiLink(link):
  contents = re.sub(r'.*\[\[(.*)\]\].*', r'\1', link).strip()
  parts = contents.split('|')
  return parts[0]

def getOwner(title):
  text = makeWikipediaRequest(title)

  inInfobox = False
  for line in text.splitlines():
    line = line.strip()
    if re.search("^[ ]*\|[ ]*(owner|company|parent)[ ]*=", line):
      parts = line.split("=")
      name = parseWikiLink(parts[1])
      if name != "":
        return getOwner(name)
  return title

company = raw_input("Company: ")
print "%s owned by %s" % (company, getOwner(company))
