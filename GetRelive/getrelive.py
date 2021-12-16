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

    #url = "https://www.relive.cc/view/vXOdKWW5p4v"
    print ("Input URL: {}".format(url))
    request = urllib.request.Request(url)
    webpage = urllib.request.urlopen(request)
    websource = webpage.read().decode("utf-8")

    regex = "((http|https)://)" + "[a-zA-Z0-9@:%._\\+~#?&//=]{2,256}" + "(mp4)"
    match = re.search (regex, websource)
    if match == None:
        print ("No matched MP4 URL")
        return
    url = match.group(0)

    #url = "https://www.relive.cc/view/vXOdKWW5p4v/mp4"
    print ("MP4 URL: {}".format(url))
    url_open=urllib.request.urlopen(url)
    url_data=url_open.read()
    redirect_path=url_open.geturl()
    print ("MP4 redirect URL: {}".format(redirect_path))

    redirect_name=redirect_path.split("/")[-1]
    outfile='C:/Remote/WorkSpace/' + redirect_name
    with open(outfile, "wb") as f:
        f.write(url_data)
    print ("Output file: {}".format(outfile))

if __name__ == '__main__':
    main()
