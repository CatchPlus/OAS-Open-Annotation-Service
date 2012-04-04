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

from StringIO import StringIO

from weightless.core import be, compose
from meresco.core import Observable

from oas import ReindexIdentifier

from testutil import joco

class ReindexIdentifierTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.observer = CallTrace(emptyGeneratorMethods=['add'])
        self.dna = be(
            (Observable(),
                (ReindexIdentifier(),
                    (self.observer, )
                )
            )
        )

    def testEmptyIdentifier(self):
        header, body = joco(self.dna.all.handleRequest(arguments={'identifier': ['']})).split('\r\n'*2, 1)
        self.assertTrue('500' in header, header)
        self.assertEquals(0, len(self.observer.calledMethods))

    def testIdentifier(self):
        self.observer.returnValues['isAvailable'] = (True, True)
        self.observer.returnValues['getStream'] = StringIO("<xml/>")
        header, body = joco(self.dna.all.handleRequest(arguments={'identifier': ['an:identifier']})).split('\r\n'*2, 1)
        self.assertTrue('200' in header, header)
        self.assertEquals(['isAvailable', 'getStream', 'add'], [m.name for m in self.observer.calledMethods])
        kwargs = self.observer.calledMethods[2].kwargs
        self.assertEquals('an:identifier', kwargs['identifier'])
        self.assertEquals('rdf', kwargs['partname'])
        self.assertTrue('lxmlNode' in kwargs)

    def testIdentifierNotFound(self):
        self.observer.returnValues['isAvailable'] = (False, False)
        header, body = joco(self.dna.all.handleRequest(arguments={'identifier': ['an:identifier']})).split('\r\n'*2, 1)
        self.assertTrue('500' in header, header)
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEquals(['isAvailable'], [m.name for m in self.observer.calledMethods])
