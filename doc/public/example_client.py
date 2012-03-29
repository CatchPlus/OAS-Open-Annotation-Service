#!/usr/bin/env python
## begin license ##
# 
# "Open Annotation Service" enables exchange, storage and search of 
# heterogeneous annotations using a uniform format (Open Annotation format) and
# a uniform web service interface. 
# 
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
# 
# This file is part of "Open Annotation Service"
# 
# "Open Annotation Service" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# "Open Annotation Service" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with "Open Annotation Service"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 
## end license ##

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

def upload(hostname='localhost', portnumber=8000, path='/update', stream=None, apiKey=None):
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
    s.send("Authorization: %s\r\n" % apiKey)
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
    args = argv[1:]
    if len(args) != 2:
        print '''Usage: %s <portnumber> <apiKey>
    Will read recorddata from stdin and post a SRUUpdate request to:
    http://localhost:<portnumber>/update
    The <apiKey> will be checked in the server'''
        exit(1)
    portnumber = int(args[0])
    apiKey = args[1]
    print upload(portnumber=portnumber, apiKey=apiKey)
