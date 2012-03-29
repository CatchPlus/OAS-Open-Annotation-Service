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

from oas.utils import identifierFromXml

from seecr.test import SeecrTestCase
from lxml.etree import parse
from StringIO import StringIO

class UtilsTest(SeecrTestCase):
    def testIdentifierFromLxmlNode(self):
        self.assertEquals(None, identifierFromXml(parse(StringIO("<xml/>"))))
        self.assertEquals("ex:Anno", identifierFromXml(parse(StringIO("""
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
            <rdf:Description rdf:about="ex:Anno">
                <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
            </rdf:Description>
        </rdf:RDF>"""))))
        self.assertEquals("ex:Anno", identifierFromXml(parse(StringIO("""
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:oas="http://www.openannotation.org/ns/">
            <oas:Annotation rdf:about="ex:Anno"/>
        </rdf:RDF>"""))))



