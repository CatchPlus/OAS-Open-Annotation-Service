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

from seecr.test import SeecrTestCase, CallTrace
from lxml.etree import parse
from StringIO import StringIO

from weightless.core import compose, be
from meresco.core import Observable

from oas import IdentifierFromXPath

class IdentifierFromXPathTest(SeecrTestCase):

    def testOne(self):
        observer = CallTrace(emptyGeneratorMethods=['add'])
        dna = be(
            (Observable(),
                (IdentifierFromXPath("/a/@b"),
                    (observer,)
                )
            )
        )

        list(compose(dna.all.add(identifier="wrong", partname="xxx", lxmlNode=parse(StringIO("<a b='right'/>")))))
        self.assertEquals("right", observer.calledMethods[0].kwargs['identifier'])


    def testTwo(self):
        observer = CallTrace(emptyGeneratorMethods=['add'])
        dna = be(
            (Observable(),
                (IdentifierFromXPath("/a/@b"),
                    (observer,)
                )
            )
        )

        try:
            list(compose(dna.all.add(identifier="wrong", partname="xxx", lxmlNode=parse(StringIO("<a x='right'/>")))))
            self.fail()
        except ValueError, e:
            self.assertEquals("Identifier not found", str(e))
