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

from seecr.test import SeecrTestCase, CallTrace

from weightless.core import be
from meresco.core import Observable

from oas import RdfTypeToField
from oas.namespaces import namespaces

from testutil import lico
from lxml.etree import parse
from StringIO import StringIO

class RdfTypeToFieldTest(SeecrTestCase):

    def setUp(self):
        SeecrTestCase.setUp(self)
        self.observer = CallTrace()
        self.dna = be(
            (Observable(),
                (RdfTypeToField(),
                    (self.observer, )
                )
            )
        )

    def testNoAnnotation(self):
        lico(self.dna.all.add(identifier="identifier", partname="partname", lxmlNode=parse(StringIO("""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"></rdf:RDF>"""))))
        self.assertEquals([], [m.name for m in self.observer.calledMethods])
    
    def testAnnotation(self):
        lico(self.dna.all.add(identifier="identifier", partname="partname", lxmlNode=parse(StringIO("""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:oa="%(oa)s"><oa:Annotation rdf:about="urn:uuid:10482225-56e3-4a5c-801b-690379aff7ac"/></rdf:RDF>""" % namespaces))))
        self.assertEquals(['addField'], [m.name for m in self.observer.calledMethods])
        self.assertEquals(dict(name="rdf:type", value="%(oa)sAnnotation" % namespaces), self.observer.calledMethods[0].kwargs)
    
    def testWithSubTypes(self):
        lico(self.dna.all.add(identifier="identifier", partname="partname", lxmlNode=parse(StringIO("""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:oa="%(oa)s">
            <oa:Annotation rdf:about="urn:uuid:10482225-56e3-4a5c-801b-690379aff7ac">
                <rdf:type rdf:resource="http://this.is.my/type"/>
                <rdf:type rdf:resource="http://this.is.my/type/to"/>
            </oa:Annotation>
        </rdf:RDF>""" % namespaces))))
        self.assertEquals(3*['addField'], [m.name for m in self.observer.calledMethods])
        self.assertEquals(dict(name="rdf:type", value="%(oa)sAnnotation" % namespaces), self.observer.calledMethods[0].kwargs)
        self.assertEquals(dict(name="rdf:type", value="http://this.is.my/type"), self.observer.calledMethods[1].kwargs)
        self.assertEquals(dict(name="rdf:type", value="http://this.is.my/type/to"), self.observer.calledMethods[2].kwargs)
