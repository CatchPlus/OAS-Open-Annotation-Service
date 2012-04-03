## begin license ##
# 
# "Open Annotation Service" enables exchange, storage and search of
# heterogeneous annotations using a uniform format (Open Annotation format) and
# a uniform web service interface. 
# 
# Copyright (C) 2012 Meertens Instituut (KNAW) http://meertens.knaw.nl
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

from amara.binderytools import bind_string
from lxml.etree import parse as parse_lxml
from StringIO import StringIO
from socket import socket
from urllib import urlencode
from cq2utils.wrappers import wrapp
from sys import stdout


def _socket(port, timeOutInSeconds):
    sok = socket()
    sok.connect(('localhost', port))
    sok.settimeout(5.0 if timeOutInSeconds is None else timeOutInSeconds)
    return sok

def createReturnValue(header, body, parse):
    if parse == True:
        try:
            body = wrapp(bind_string(body))
        except:
            print 'parsing failed for:' + str(body)
            raise
    elif parse == 'lxml':
        if body:
            try:
                body = parse_lxml(StringIO(body))
            except:
                print 'parsing failed for:', body
                raise

    return header, body

def postRequest(port, path, data, contentType='text/xml; charset="utf-8"', parse=True, timeOutInSeconds=None, additionalHeaders=None):
    additionalHeaders = additionalHeaders or {}
    sok = _socket(port, timeOutInSeconds)
    try:
        contentLength = len(data)
        lines = [
            'POST %(path)s HTTP/1.0',
            'Content-Type: %(contentType)s',
            'Content-Length: %(contentLength)s'
        ]
        lines += ["%s: %s" % (k, v) for k, v in additionalHeaders.items()]
        lines += ['', '']
        sendBuffer = ('\r\n'.join(lines) % locals()) + data
        totalBytesSent = 0
        bytesSent = 0
        while totalBytesSent != len(sendBuffer):
            bytesSent = sok.send(sendBuffer[totalBytesSent:])
            totalBytesSent += bytesSent

        header, body = receiveFromSocket(sok)
        return createReturnValue(header, body, parse)
    finally:
        sok.close()

def postMultipartForm(port, path, formValues, parse=True, timeOutInSeconds=None):
    boundary = '-=-=-=-=-=-=-=-=TestBoundary1234567890'
    body = createPostMultipartForm(boundary, formValues)
    return postRequest(port, path, body, contentType='multipart/form-data; boundary=' + boundary, parse=parse, timeOutInSeconds=timeOutInSeconds)

def createPostMultipartForm(boundary, formValues):
    strm = StringIO()
    for valueDict in formValues:
        fieldType = valueDict['type']
        headers = {}
        headers['Content-Disposition'] = 'form-data; name="%(name)s"' % valueDict
        if fieldType == 'file':
            headers['Content-Disposition'] = headers['Content-Disposition'] + '; filename="%(filename)s"' % valueDict
            headers['Content-Type'] = valueDict['mimetype']

        strm.write('--' + boundary + '\r\n')
        for item in headers.items():
            strm.write('%s: %s\r\n' % item)
        strm.write('\r\n')
        strm.write(valueDict['value'])
        strm.write('\r\n')
    strm.write('--' + boundary + '--\r\n')

    return strm.getvalue()

def getRequest(port, path, arguments=None, parse=True, timeOutInSeconds=None, host=None, additionalHeaders=None):
    sok = _socket(port, timeOutInSeconds)
    try:
        requestString = path
        if arguments:
            requestString = path + '?' + urlencode(arguments, doseq=True)

        request = 'GET %(requestString)s HTTP/1.0\r\n' % locals()
        if host != None:
            request = 'GET %(requestString)s HTTP/1.1\r\nHost: %(host)s\r\n' % locals()
        if additionalHeaders != None:
            for header in additionalHeaders.items():
                request += '%s: %s\r\n' % header
        request += '\r\n'
        sok.send(request)
        header, body = receiveFromSocket(sok)
        return createReturnValue(header, body, parse)
    finally:
        sok.close()


def receiveFromSocket(sok):
    response = ''
    part = sok.recv(1024)
    response += part
    while part != None:
        part = sok.recv(1024)
        if not part:
            break
        response += part
    return response.split('\r\n\r\n', 1)


def headerToDict(header):
   return dict(
       tuple(s.strip() for s in line.split(':')) 
       for line in header.split('\r\n')
       if ':' in line
   )

