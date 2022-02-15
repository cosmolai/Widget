#!/usr/bin/env python3

import sys
import re
import urllib.request

def main():
    #print (sys.argv)
    if len(sys.argv) < 2:
        print ("Input URL is empty")
        return
    url = sys.argv[1]

    # open input url and get web source
    print ("Input URL: {}".format(url))
    request = urllib.request.Request(url)
    webpage = urllib.request.urlopen(request)
    websource = webpage.read().decode("utf-8")

    # get mp4 url
    regex = "((http|https)://)" + "[a-zA-Z0-9@:%._\\+~#?&//=]{2,256}" + "(mp4)"
    match = re.search (regex, websource)
    if match == None:
        print ("No matched MP4 URL")
        return
    url = match.group(0)

    # download mp4 file
    print ("MP4 URL: {}".format(url))
    url_open=urllib.request.urlopen(url)
    url_data=url_open.read()
    redirect_path=url_open.geturl()
    print ("MP4 redirect URL: {}".format(redirect_path))

    redirect_name=redirect_path.split("/")[-1]

    # get date and description from web source
    regex = "(<h2>)" + ".*" + "(</h2>)"
    match = re.search (regex, websource)
    description = ""
    if match != None:
        description = match.group(0)
        description = description.replace("<h2>", "")
        description = description.replace("</h2>", "")
    print ("Description: {}".format(description))
    regex = '("media":\[\],"moment_at":)' + '"[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\.[0-9][0-9][0-9]Z"'
    match = re.search (regex, websource)
    date = ""
    if match != None:
        regex = "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]"
        match = re.search(regex, match.group(0))
        if match != None:
            date = match.group(0)
            date = date.replace("-", "")
    print ("Date: {}".format(date))

    # output
    outfile = date + description + redirect_name
    with open(outfile, "wb") as f:
        f.write(url_data)
    print ("Output file: {}".format(outfile))

if __name__ == '__main__':
    main()
