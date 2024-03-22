# gallery.py
# Author: Nils Knieling - https://github.com/Cyclenerd/gallery_shell
# Inspired by: Shapor Naghibzadeh - https://github.com/shapor/bashgal
# Port to python: sdasda7777

#########################################################################################
#### Configuration Section
#########################################################################################
import getopt
import os
import re
import subprocess
import sys
import time
from shutil import which

MY_HEIGHT_SMALL=187
MY_HEIGHT_LARGE=768
MY_QUALITY=85
MY_THUMBDIR="__thumbs"
MY_INDEX_HTML_FILE="index.html"
MY_TITLE="Gallery"
MY_FOOTER='Created with <a href="https://github.com/sdasda7777/gallery_py">gallery.py</a>'

# Use convert from ImageMagick
MY_CONVERT_COMMAND="convert" 
# Use JHead for EXIF Information
MY_EXIF_COMMAND="jhead"

# Bootstrap 4
MY_CSS="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.6.0/css/bootstrap.min.css"

# Debugging output
# True=enable, False=disable 
MY_DEBUG=True

#########################################################################################
#### End Configuration Section
#########################################################################################

MY_SCRIPT_NAME=os.path.basename(os.path.normpath(sys.argv[0]))
MY_DATETIME=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())  #2021-10-17 15:35:19

def usage(code):
	print("Usage: "+MY_SCRIPT_NAME+" [-t <title>] [-d <thumbdir>] [-h]:\n\t[-t <title>]\t sets the title (default: "+MY_TITLE+")\n\t[-d <thumbdir>]\t sets the thumbdir (default: "+MY_THUMBDIR+")\n\t[-h]\t\t displays help (this message)")
	sys.exit(code)

def debugOutput(text):
	if MY_DEBUG:
		print(text) # if debug variable is True, echo whatever's passed to the function

def getFileSize(path):
	return "{:.2f} MB".format(float(os.path.getsize(path)) / 1024 / 1024)

optlist, arglist = getopt.getopt(sys.argv[1:], "t:d:h")
for o, v in optlist:
	if o == "-t":
		MY_TITLE = v
	elif o == "-d":
		MY_THUMBDIR = v
	elif o == "-h":
		usage(0)
	else:
		usage(1)

debugOutput("- " + MY_SCRIPT_NAME + " : " + MY_DATETIME)

### Check Commands
if not which(MY_CONVERT_COMMAND):
	print("!!! "+MY_CONVERT_COMMAND+" is not installed.  Aborting.")
	sys.exit(1)
if not which(MY_EXIF_COMMAND):
	print("!!! "+MY_EXIF_COMMAND+" is not installed.  Aborting.")
	sys.exit(1)

### Create Folders
if not os.path.isdir(MY_THUMBDIR):
	os.mkdir(MY_THUMBDIR)

MY_HEIGHTS = []
MY_HEIGHTS.append(MY_HEIGHT_SMALL)
MY_HEIGHTS.append(MY_HEIGHT_LARGE)
for MY_RES in MY_HEIGHTS:
	if not os.path.isdir(MY_THUMBDIR+"/"+str(MY_RES)):
		os.mkdir(MY_THUMBDIR+"/"+str(MY_RES))

#### Create Startpage
debugOutput(MY_INDEX_HTML_FILE)
indexHTMLFile = open(MY_INDEX_HTML_FILE, 'w')
indexHTMLFile.write(
"<!DOCTYPE HTML>\n\
<html lang=\"en\">\n\
<head>\n\
	<meta charset=\"utf-8\">\n\
	<title>"+MY_TITLE+"</title>\n\
	<meta name=\"viewport\" content=\"width=device-width\">\n\
	<meta name=\"robots\" content=\"noindex, nofollow\">\n\
	<link rel=\"stylesheet\" href=\""+MY_CSS+"\">\n\
</head>\n\
<body>\n\
<header>\n\
	<div class=\"navbar navbar-dark bg-dark shadow-sm\">\n\
		<div class=\"container\">\n\
			<a href=\"#\" class=\"navbar-brand\">\n\
				<strong>"+MY_TITLE+"</strong>\n\
			</a>\n\
			\n\
			<select onchange=\"sortPictures()\" id=\"sort-combo\">\n\
				<option value=\"1\">Date, ascending\n\
				<option value=\"2\" selected>Date, descending\n\
				<option value=\"3\">Size, ascending\n\
				<option value=\"4\">Size, descending\n\
				<option value=\"5\">Name, ascending\n\
				<option value=\"6\">Name, descending\n\
			</select>\n\
		</div>\n\
	</div>\n\
</header>\n\
<main class=\"container\">\n")

### Photos (JPG)
jpgs = [x for x in os.listdir() if re.match("^.*\.[jJ][pP][eE]?[gG]$", x)]

jpgsByName = []
jpgsBySize = []
jpgsByDate = []

if len(jpgs) > 0:
	indexHTMLFile.write('<div class="row row-cols-sm-1 row-cols-md-2 row-cols-lg-3 row-cols-xl-4 py-5" id="thumbnail-container">\n')
	## Generate Images

	for MY_FILENAME in jpgs:
		for MY_RES in MY_HEIGHTS:
			if not os.path.exists(MY_THUMBDIR+"/"+str(MY_RES)+"/"+MY_FILENAME) or os.path.getsize(MY_THUMBDIR+"/"+str(MY_RES)+"/"+MY_FILENAME) == 0:
				debugOutput(MY_THUMBDIR+"/"+str(MY_RES)+"/"+MY_FILENAME)
				subprocess.run((MY_CONVERT_COMMAND+" -auto-orient -strip -quality "+str(MY_QUALITY)+" -resize x"+str(MY_RES)+" "+MY_FILENAME
				+" "+MY_THUMBDIR+"/"+str(MY_RES)+"/"+MY_FILENAME).split())
		
		MY_EXIF_INFO=subprocess.check_output([MY_EXIF_COMMAND, MY_FILENAME]).decode("utf-8")
		exifInfoForSorting = MY_EXIF_INFO.split("\n")
		
		jpgsByName.append((MY_FILENAME, exifInfoForSorting[0][15:]))
		jpgsBySize.append((MY_FILENAME, int(exifInfoForSorting[1][15:-6])))
		jpgsByDate.append((MY_FILENAME, exifInfoForSorting[2][15:]))		

	jpgsByName.sort(key=lambda y: y[1].lower())
	jpgsBySize.sort(key=lambda y: y[1])
	jpgsByDate.sort(key=lambda y: y[1])

	for MY_FILENAME in jpgs:
		name = [i for i, t in enumerate(jpgsByName) if t[0] == MY_FILENAME][0]
		size = [i for i, t in enumerate(jpgsBySize) if t[0] == MY_FILENAME][0]
		date = [i for i, t in enumerate(jpgsByDate) if t[0] == MY_FILENAME][0]
		
		indexHTMLFile.write(
		"<div class=\"col\" sort-info-name=\""+str(name)+"\" sort-info-size=\""+str(size)+"\" sort-info-date=\""+str(date)+"\"><p>\n\
		<a href=\""+MY_THUMBDIR+"/"+MY_FILENAME+".html\"><img src=\""+MY_THUMBDIR+"/"+str(MY_HEIGHT_SMALL)+"/"+MY_FILENAME+"\" alt=\"Thumbnail: "+MY_FILENAME+"\" class=\"rounded mx-auto d-block\" style=\"width: 100%;\"></a>\n</p></div>\n")
		
		prevByName=""
		nextByName=""
		prevBySize=""
		nextBySize=""
		prevByDate=""
		nextByDate=""
		
		if name != 0:
			prevByName = jpgsByName[name - 1][0]
		if name != len(jpgs) - 1:
			nextByName = jpgsByName[name + 1][0]
		if size != 0:
			prevBySize = jpgsBySize[size - 1][0]
		if size != len(jpgs) - 1:
			nextBySize = jpgsBySize[size + 1][0]
		if date != 0:
			prevByDate = jpgsByDate[date - 1][0]
		if date != len(jpgs) - 1:
			nextByDate = jpgsByDate[date + 1][0]
			
		MY_IMAGE_HTML_FILE=MY_THUMBDIR+"/"+MY_FILENAME+".html"
		MY_FILESIZE=getFileSize(MY_FILENAME)
		debugOutput(MY_IMAGE_HTML_FILE)
		imageHTMLFile = open(MY_IMAGE_HTML_FILE, 'w')
		imageHTMLFile.write(
		"<!DOCTYPE HTML>\n\
		<html lang=\"en\">\n\
		<head>\n\
		<meta charset=\"utf-8\">\n\
		<title>"+MY_FILENAME+"</title>\n\
		<meta name=\"viewport\" content=\"width=device-width\">\n\
		<meta name=\"robots\" content=\"noindex, nofollow\">\n\
		<link rel=\"stylesheet\" href=\""+MY_CSS+"\">\n\
		</head>\n\
		<body>\n\
			<header>\n\
				<div class=\"navbar navbar-dark bg-dark shadow-sm\">\n\
					<div class=\"container\">\n\
						<a href=\"../index.html\" class=\"navbar-brand\">\n\
							<strong>"+MY_TITLE+"</strong>\n\
						</a>\n\
					</div>\n\
				</div>\n\
			</header>\n\
		<main class=\"container\">\n")

		# Pager
		imageHTMLFile.write("<div class=\"row py-3\"><div class=\"col text-left\" id=\"gallery-scroll-left\">")
		if prevByName != "":
			imageHTMLFile.write('<a href="'+prevByName+'.html" accesskey="p" title="⌨️ PC: [Alt]+[Shift]+[P] / MAC: [Control]+[Option]+[P]" class="btn btn-secondary " role="button">&laquo; Previous</a>')
		else:
			imageHTMLFile.write('<a href="#" class="btn btn-secondary  disabled" role="button" aria-disabled="true">&laquo; Previous</a>')

		imageHTMLFile.write("</div><div class=\"col d-none d-md-block text-center\"><h3>"+MY_FILENAME+"</h3></div><div class=\"col text-right\" id=\"gallery-scroll-right\">")
		
		if nextByName != "":
			imageHTMLFile.write('<a href="'+nextByName+'.html" accesskey="n" title="⌨️ PC: [Alt]+[Shift]+[N] / MAC: [Control]+[Option]+[N]" class="btn btn-secondary ">Next &raquo;</a>')
		else:
			imageHTMLFile.write('<a href="#" class="btn btn-secondary  disabled" role="button" aria-disabled="true">Next &raquo;</a>')

		imageHTMLFile.write('</div></div>')

		imageHTMLFile.write(
		"<div class=\"row\">\
			<div class=\"col\">\
				<p><img src=\""+str(MY_HEIGHT_LARGE)+"/"+MY_FILENAME+"\" class=\"img-fluid\" alt=\"Image: "+MY_FILENAME+"\"></p>\
			</div>\
		</div>\
		<div class=\"row\">\
			<div class=\"col\">\
				<p><a class=\"btn btn-primary\" href=\"../"+MY_FILENAME+"\">Download Original ("+MY_FILESIZE+")</a></p>\
			</div>\
		</div>")

		# EXIF
		if len(MY_EXIF_INFO) > 0:
			imageHTMLFile.write("<div class=\"row\"><div class=\"col\"><pre>"+MY_EXIF_INFO+"</pre></div></div>")

		# Footer
		imageHTMLFile.write(
		"<script>let neighbors = [\""+prevByName+"\", \""+nextByName+"\", \""
		+prevBySize+"\", \""+nextBySize+"\", \""+prevByDate+"\", \""+nextByDate+"\"];\n\
	let residualSort = window.location.search.substr(1);\n\
	if(residualSort.length == 2){\n\
		let sortType = [\"n\", \"s\", \"d\"].indexOf(residualSort[0]);\n\
		let sortOrder = [\"a\",\"d\"].indexOf(residualSort[1]);\n\
		prev = 2*sortType+(sortOrder==0?0:1);\n\
		next = 2*sortType+(sortOrder==0?1:0);\n\
		if(neighbors[prev] != \"\"){\n\
			document.getElementById(\"gallery-scroll-left\").innerHTML = \"<a href=\\\"\"+neighbors[prev]+\".html?\"+residualSort+\"\\\" accesskey=\\\"p\\\" title=\\\"⌨️ PC: [Alt]+[Shift]+[P] / MAC: [Control]+[Option]+[P]\\\" class=\\\"btn btn-secondary \\\" role=\\\"button\\\">&laquo; Previous</a>\"\n\
		}else{\n\
			document.getElementById(\"gallery-scroll-left\").innerHTML = \"<a href=\\\"#\\\" class=\\\"btn btn-secondary  disabled\\\" role=\\\"button\\\" aria-disabled=\\\"true\\\">&laquo; Previous</a>\"\n\
		}\n\
		if(neighbors[next] != \"\"){\n\
			document.getElementById(\"gallery-scroll-right\").innerHTML = \"<a href=\\\"\"+neighbors[next]+\".html?\"+residualSort+\"\\\" accesskey=\\\"n\\\" title=\\\"⌨️ PC: [Alt]+[Shift]+[N] / MAC: [Control]+[Option]+[N]\\\" class=\\\"btn btn-secondary \\\">Next &raquo;</a>\"\n\
		}else{\n\
			document.getElementById(\"gallery-scroll-right\").innerHTML = \"<a href=\\\"#\\\" class=\\\"btn btn-secondary  disabled\\\" role=\\\"button\\\" aria-disabled=\\\"true\\\">Next &raquo;</a>\"\n\
		}\n\
	}\n\
</script>\
		</main> <!-- // main container --><br><footer class=\"footer mt-auto py-3 bg-light\"><div class=\"container\">\
			<span class=\"text-muted\">"+MY_FOOTER+" - "+MY_DATETIME+"</span>\
		</div></footer></body></html>")
		imageHTMLFile.close()
		
	indexHTMLFile.write(
	"</div><script>\n\
function sortPictures(){\n\
	let list = document.getElementById(\"thumbnail-container\");\n\n\
	let items = list.childNodes;\n\
	let itemsArr = [];\n\
	for (let i in items) {\n\
		if (items[i].nodeType == 1) { // get rid of the whitespace text nodes\n\
		    itemsArr.push(items[i]);\n\
		}\n\
	}\n\n\
	let sortType = parseInt(document.getElementById(\"sort-combo\").value);\n\
	itemsArr.sort(function(a, b) {\n\n\
		if(sortType > 0 && sortType <= 6){\n\
			let paramName =	\"sort-info-\" + [\"date\", \"size\", \"name\"][Math.floor((sortType-1)/2)];\n\
			if(parseInt(a.getAttribute(paramName)) == parseInt(b.getAttribute(paramName))) return 0;\n\
			if((sortType % 2 == 0 && parseInt(a.getAttribute(paramName)) < parseInt(b.getAttribute(paramName)))\n\
				|| (sortType % 2 == 1 && parseInt(a.getAttribute(paramName)) > parseInt(b.getAttribute(paramName)))) return 1;\n\
			return -1;\n\
		}\n\
		return 0;\n\
	});\n\n\
	\
	let paramLetter = [\"d\", \"s\", \"n\"][Math.floor((sortType-1)/2)];\
	let sortLetter = [\"a\", \"d\"][(sortType + 1) % 2];\
	\
	for (i = 0; i < itemsArr.length; ++i) {\n\
		let link = itemsArr[i].querySelectorAll(\"p > a\")[0];\n\
		if(link.href[link.href.length-3] == \"?\"){\n\
			link.href = link.href.substring(0, link.href.length-2);\n\
			link.href += paramLetter + sortLetter;\n\
		}else{\n\
			link.href += \"?\" + paramLetter + sortLetter;\n\
		}\n\
		list.appendChild(itemsArr[i]);\n\
	}\n}\n\nsortPictures();\n</script>\n")


### Movies (MOV or MP4)
videos = [x for x in os.listdir() if re.match("^.*\.(mov|mp4)$", x)]
if len(videos) > 0:
	indexHTMLFile.write(
	"<div class=\"row\"><div class=\"col\">\n\
	<div class=\"page-header\"><h2>Movies</h2></div>\n\
</div></div>\n\
<div class=\"row\"><div class=\"col\">\n")

	for MY_FILENAME in videos:
		indexHTMLFile.write("<a href=\""+MY_FILENAME+"\" class=\"btn btn-primary\" role=\"button\">"+MY_FILENAME+" ("+getFileSize(MY_FILENAME)+")</a>\n")

	indexHTMLFile.write("</div></div>\n")


### Downloads (ZIP)
zips = [x for x in os.listdir() if re.match("^.*\.zip$", x)]
if len(zips) > 0:
	indexHTMLFile.write(
	"<div class=\"row\"><div class=\"col\">\n\
	<div class=\"page-header\"><h2>Downloads</h2></div>\n\
</div></div>\n\
<div class=\"row\"><div class=\"col\">\n")

	for MY_FILENAME in zips:
		indexHTMLFile.write("<a href=\""+MY_FILENAME+"\" class=\"btn btn-primary\" role=\"button\">"+MY_FILENAME+" ("+getFileSize(MY_FILENAME)+")</a>\n")

	indexHTMLFile.write("</div></div>\n")

### Footer
indexHTMLFile.write(
"</main> <!-- // main container -->\n\
<br>\n\
<footer class=\"footer mt-auto py-3 bg-light\">\n\
	<div class=\"container\">\n\
		<span class=\"text-muted\">"+MY_FOOTER+" - "+MY_DATETIME+"</span>\n\
	</div>\n\
</footer>\n\
</body>\n\
</html>\n")
indexHTMLFile.close()

debugOutput("= done")
