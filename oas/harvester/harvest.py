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

from lxml.etree import parse, ElementTree, tostring
from urllib2 import urlopen
from meresco.core import Observable
from oas.namespaces import xpath


class Harvest(Observable):
    def process(self, repository):
        try:
            lxmlNode = parse(self._urlopen(repository.listRecordsUrl()))
        except Exception, e:
            repository.logException(e)
            return
        errors = xpath(lxmlNode, "/oai:OAI-PMH/oai:error")
        if len(errors) > 0:
            for error in errors:
                repository.logError("%s: %s" % (error.get("code"), error.text))
            repository.resumptionToken = None
            repository.save()
            return
        try:
            verbNode = xpath(lxmlNode, "/oai:OAI-PMH/oai:ListRecords")[0]
            for item in xpath(verbNode, 'oai:record'):
                header = xpath(item, 'oai:header')[0]
                identifier = xpath(header, 'oai:identifier/text()')[0]
                if header.attrib.get('status', None) == 'deleted':
                    yield self.all.delete(identifier=identifier)
                    continue
                yield self.all.add(identifier=identifier, lxmlNode=ElementTree(item))
            repository.resumptionToken = ''.join(xpath(verbNode, "oai:resumptionToken/text()"))
            if not repository.resumptionToken:
                repository.active = False
        finally:
            repository.save()

    def _urlopen(self, *args, **kwargs):
        return urlopen(*args, **kwargs)
