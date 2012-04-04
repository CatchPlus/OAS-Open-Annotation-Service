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

from weightless.core import be, compose
from meresco.core import Observable

from testutil import lico
from StringIO import StringIO

from oas import OaiUserSet

class OaiUserSetTest(SeecrTestCase):
    def testOne(self):
        observer = CallTrace(
            returnValues={
                'getForApiKey': {'username': 'my_user'},
                'isAvailable': (True, True),
                'getStream': StringIO('my_user')
                })
        dna = be(
            (Observable(),
                (OaiUserSet(),
                    (observer, )
                )
            )
        )

        dna.do.addOaiRecord(identifier="identifier", sets=None, metadataFormats=None)

        self.assertEquals(['isAvailable', 'getStream', 'addOaiRecord'], [m.name for m in observer.calledMethods])

        addCall = observer.calledMethods[2]
        self.assertEquals(set([('my_user', 'my_user')]), addCall.kwargs['sets'])
