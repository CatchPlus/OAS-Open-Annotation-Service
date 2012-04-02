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

from weightless.core import be, compose
from meresco.components.http.utils import unauthorizedHtml
from meresco.core import Observable

from oas import ApiKeyCheck

class ApiKeyCheckTest(SeecrTestCase):
    def testOne(self):
        dna = be(
            (Observable(),
                (ApiKeyCheck(),)
            )
        )

        response = list(compose(dna.all.handleRequest()))
        self.assertEquals([unauthorizedHtml], response)

    def testUnknownApiKey(self):
        def getForApiKey(apiKey):
            return None
        observer = CallTrace(
            methods={'getForApiKey': getForApiKey}, 
            emptyGeneratorMethods=['handleRequest'])

        __callstack_var_authorization__ = {'apiKey': "APIKEY"}

        dna = be(
            (Observable(),
                (ApiKeyCheck(),
                    (observer, )
                )
            )
        )
        response = list(compose(dna.all.handleRequest()))
        self.assertEquals([unauthorizedHtml], response)
        self.assertEquals(['getForApiKey'], [m.name for m in observer.calledMethods])

    def testUnknownApiKeyForAdd(self):
        def getForApiKey(apiKey):
            return None
        observer = CallTrace(
            methods={'getForApiKey': getForApiKey}, 
            emptyGeneratorMethods=['add'])

        __callstack_var_authorization__ = {'apiKey': "APIKEY"}

        dna = be(
            (Observable(),
                (ApiKeyCheck(),
                    (observer, )
                )
            )
        )
        self.assertRaises(ValueError, lambda: list(compose(dna.all.add(identifier='bla'))))
        self.assertEquals(['getForApiKey'], [m.name for m in observer.calledMethods])
