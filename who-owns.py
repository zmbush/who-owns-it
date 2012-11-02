import urllib2
import urllib
import json
import re
import sys


companies = {}
def loadCompanyFile(filename):
  retval = {}
  open(filename, 'a').close()
  f = open(filename)
  for line in f:
    parts = line.strip().split('\x00')
    retval[parts[0].decode('utf-8')] = parts[1].decode('utf-8')
  return retval
  f.close()

def writeCompanyFile(filename, data):
  f = open(filename, 'w')
  for company, owner in data.iteritems():
    f.write("%s\x00%s\n" % (company.encode('utf-8'), owner.encode('utf-8')))
  f.close()

def makeWikipediaRequest(title):
  data = {
    "format" : "json",
    "action" : "query",
    "prop"   : "revisions",
    "rvprop" : "content",
    "titles" : re.sub(" ", "_", title)
  }

  data = dict([k.encode('utf-8'), v.encode('utf-8')] for k,v in data.items())
  url =  "http://en.wikipedia.org/w/api.php?%s" % urllib.urlencode(data)

  text = json.loads(urllib2.urlopen(url).read())

  pages = text["query"]["pages"]
  page = pages.values()[0]
  if "missing" not in page:
    revisions = page["revisions"]
    data = revisions[0]
    text = data["*"]
  else:
    text = None

  return text

def parseWikiLink(link):
  retval = ""
  if re.match('.*\[\[.*\]\].*', link):
    contents = re.sub(r'.*\[\[(.*)\]\].*', r'\1', link).strip()
    parts = contents.split('|')
    retval = parts[0]
  elif re.match('.*\[.*\].*', link):
    contents = re.sub(r'.*\[(.*)\].*', r'\1', link).strip()
    retval = contents[contents.index(" "):].strip()
  else:
    retval = re.sub(r'\(.*\)', '', link).strip()
  return retval

def getMostRecentCompany(text):
  companies = text.split("<br />")
  return parseWikiLink(companies[-1])

def getOwner(title):
  print "Getting owner of: " + title

  text = makeWikipediaRequest(title)
  if text == None:
    return (title, [title])

  inInfobox = False

  if "{{disambig}}" in text or "{{disambiguation}}" in text:
    print "Did you mean:"
    disamb = []
    for line in text.splitlines():
      if line.startswith("*"):
        link = parseWikiLink(line)
        disamb.append(link)
        print "% 3d) %s" % (len(disamb), link)
    selection = int(raw_input("Enter Selection: ")) - 1
    if selection < len(disamb):
      owner, path = getOwner(disamb[selection])
      path.append(title)
      return (owner, path)
  else:
    for line in text.splitlines():
      line = line.strip()
      if re.search("^[ ]*\|[ ]*((current|)owner|company|parent|developer)[ ]*=", line):
        parts = line.split("=")
        name = getMostRecentCompany(parts[1])
        if name != "":
          owner, path = getOwner(name)
          companies[title] = name
          path.append(title)
          return (owner, path)
      if re.search("^[ ]*#(redirect|Redirect|REDIRECT)[ ]*(\[\[.*\]\])", line):
        link = line[line.index("[")-1:]
        redirect = parseWikiLink(link)
        companies[title] = redirect
        return getOwner(redirect)
  return (title, [title])

companies = loadCompanyFile("companies.cache")
company = ""
if len(sys.argv) > 1:
  company = ' '.join(sys.argv[1:])
else:
  company = raw_input("Company: ")
owner, path = getOwner(company)
print "%s is owned by %s" % (company, owner)
print "   %s" % (' -> '.join(reversed(path)))
writeCompanyFile("companies.cache", companies)
