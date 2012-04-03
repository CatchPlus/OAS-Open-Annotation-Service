#!/usr/bin/env python
## begin license ##
# 
# "Open Annotation Service" enables exchange, storage and search of
# heterogeneous annotations using a uniform format (Open Annotation format) and
# a uniform web service interface. 
# 
# Copyright (C) 2011-2012 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2012 Meertens Instituut (KNAW) http://meertens.knaw.nl
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

from urllib import urlopen, urlencode
from urlparse import urlsplit
from cgi import parse_qs
from lxml.etree import parse, tostring
from os.path import isfile
from xml.sax.saxutils import escape as xmlEscape
from sys import exit

SRUUPLOADURL="http://openindex.dev.seecr.nl:8000/update"

SRUURL="http://jsru.kb.nl/sru/GGC"
BASEURL="http://services.kb.nl/mdo/oai"
QUERY="type=Sound"
STARTRECORDFILE="startRecord.txt"
META_TEMPLATE=open("meta.xml").read()
SRURECORDUPDATE_TEMPLATE=open("sruRecordUpdate.xml").read()

def sruQuery(startRecord=1):
    return "%s?%s" % (SRUURL, urlencode(dict(
        version="1.1", 
        query=QUERY, 
        recordSchema="dcx", 
        operation="searchRetrieve", 
        startRecord=startRecord)))


def downloadSru(startRecord=1):
    return parse(urlopen(sruQuery(startRecord=startRecord)))

def readStartRecord():
    return int(open(STARTRECORDFILE).read()) if isfile(STARTRECORDFILE) else 1

def writeStartRecord(startRecord):
    open(STARTRECORDFILE, "w").write(str(startRecord))

def xpath(node, xpathExpression):
    return node.xpath(xpathExpression, namespaces={
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'srw': "http://www.loc.gov/zing/srw/",
        'srw_dc': "info:srw/schema/1/dc-v1.1",
        'tel': "http://krait.kb.nl/coop/tel/handbook/telterms.html", 
        'ucp': "info:lc/xmlns/update-v1",
        'dc': "http://purl.org/dc/elements/1.1/",
        'dcterms': "http://purl.org/dc/terms/", 
        'dcx': "http://krait.kb.nl/coop/tel/handbook/telterms.html"})

def getIdentifier(dcxRecord):
    uri = xpath(dcxRecord, 'dc:identifier[@xsi:type="dcterms:URI"]/text()')[0]
    scheme, netloc, path, query, fragments = urlsplit(uri)
    args = parse_qs(query)
    PPN, identifier = args['urn'][0].split(':', 1)
    return ':'.join(['GGC', 'AC', identifier])

def createMeta(**kwargs):
    return META_TEMPLATE % kwargs

def createSruRecordUpdate(**kwargs):
    return SRURECORDUPDATE_TEMPLATE % kwargs

def createDocument(**kwargs):
    yield '<document xmlns="http://meresco.org/namespace/harvester/document">'
    for name, contents in kwargs.items():
        yield '<part name="%s">%s</part>' % (xmlEscape(name), xmlEscape(contents))
    yield '</document>'


def sruRecordUpload(sruRecordUpdate):
    response = parse(urlopen(SRUUPLOADURL, sruRecordUpdate))
    operationStatus = xpath(response, "/srw:updateResponse/ucp:operationStatus/text()")[0]
    if operationStatus != "success":
        print tostring(response)
        exit(1)


def main():
    startRecord = readStartRecord()

    while True:
        sruResponse = downloadSru(startRecord)
        numberOfRecords = int(xpath(sruResponse, '/srw:searchRetrieveResponse/srw:numberOfRecords/text()')[0])
        print startRecord, numberOfRecords
        dcxRecords = xpath(sruResponse, '/srw:searchRetrieveResponse/srw:records/srw:record/srw:recordData/srw_dc:dc')
        for dcxRecord in dcxRecords:
            identifier = getIdentifier(dcxRecord)
            print "Uploading", identifier
            document = '\n'.join(createDocument(
                meta=createMeta(identifier=identifier), 
                record=tostring(dcxRecord)))
            sruRecordUpload(createSruRecordUpdate(
                recordIdentifier='kb_gcc:%s' % identifier, 
                recordData=document))
            startRecord += 1
        writeStartRecord(startRecord)
        if startRecord == numberOfRecords:
            break



if __name__ == '__main__':
    main()
