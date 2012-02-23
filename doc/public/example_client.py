#!/usr/bin/env python

from os import system                               #DO_NOT_DISTRIBUTE
from glob import glob                               #DO_NOT_DISTRIBUTE
from sys import path as systemPath                  #DO_NOT_DISTRIBUTE
system('find .. -name "*.pyc" | xargs rm -f')       #DO_NOT_DISTRIBUTE
for path in glob('../deps.d/*'):                    #DO_NOT_DISTRIBUTE
    systemPath.insert(0, path)                      #DO_NOT_DISTRIBUTE
systemPath.insert(0, '..')                          #DO_NOT_DISTRIBUTE

from sys import stdin, argv
from socket import socket
from lxml.etree import parse, tostring

from oas.namespaces import xpath

def upload(hostname='localhost', portnumber=8000, path='/update', stream=None):
    # Try parsing the input. If the supplied XML is invalid this will fail.
    try:
        lxmlNode = parse(stream if stream else stdin)
    except Exception, e:
        print "Error parsing input:", str(e)
        exit(1)

    # construct the body, insert the identifier and supplied XML.
    body = """<ucp:updateRequest xmlns:ucp="info:lc/xmlns/update-v1">
        <srw:version xmlns:srw="http://www.loc.gov/zing/srw/">1.0</srw:version>
        <ucp:action>info:srw/action/1/replace</ucp:action>
        <ucp:recordIdentifier>IGNORED</ucp:recordIdentifier>
        <srw:record xmlns:srw="http://www.loc.gov/zing/srw/">
            <srw:recordPacking>xml</srw:recordPacking>
            <srw:recordSchema>rdf</srw:recordSchema>
            <srw:recordData>%s</srw:recordData>
        </srw:record>
    </ucp:updateRequest>""" % tostring(lxmlNode)

     # Connect to the server and send the update request.
    s = socket()
    s.connect((hostname, portnumber))
    s.send("POST %s HTTP/1.0\r\n" % path)
    s.send("Content-Type: text/xml\r\n")
    s.send("Content-Length: %s\r\n" % len(body))
    s.send("\r\n")
    s.sendall(body)

    # Receive the answer from the server and print it to stdout.
    response = s.recv(1024)
    while True:
        part = s.recv(1024)
        if part == "":
            break
        response += part
    s.close()
    return response

if __name__ == '__main__':
    portnumber = 8000
    if len(argv) > 1 and argv[1].isdigit():
        portnumber = int(argv[1])
    print upload(portnumber=portnumber)
