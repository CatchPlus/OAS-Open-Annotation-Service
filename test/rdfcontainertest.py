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

from seecr.test import SeecrTestCase
from lxml.etree import parse
from StringIO import StringIO

from oas import RdfContainer
from oas.namespaces import getAttrib

class RdfContainerTest(SeecrTestCase):

    def testOne(self):
        XML = """<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:oac="http://www.openannotation.org/ns/">
    <rdf:Description rdf:about="urn:nr:1"/>
    <rdf:Description rdf:about="urn:nr:2"/>
    <rdf:Description rdf:about="urn:nr:3"/>
    <rdf:Description rdf:about="urn:nr:4"/>
</rdf:RDF>"""

        container = RdfContainer(parse(StringIO(XML)))
        result = container.resolve('urn:nr:3')
        self.assertEquals('urn:nr:3', getAttrib(result, "rdf:about"))
