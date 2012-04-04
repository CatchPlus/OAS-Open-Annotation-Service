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

from seecr.test import CallTrace, SeecrTestCase
from weightless.core import compose

from oas.adduserdatafromapikey import AddUserDataFromApiKey

from testutil import lico

class AddUserDataFromApiKeyTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.retrieve = AddUserDataFromApiKey()
        self.observer = CallTrace('observer')
        self.retrieve.addObserver(self.observer)

    def testNoApiKey(self):
        self.assertRaises(AttributeError, lambda: lico(self.retrieve.add(identifier='identifier', partname='rdf', data='RDF')))

    def testApiKeyRetrieves(self):
        self.observer.returnValues['getForApiKey'] = {'username': 'User Name'}
        self.observer.emptyGeneratorMethods.append('add')
        __callstack_var_authorization__ = {'apiKey': 'MonkeyWrench'}
        lico(self.retrieve.add(identifier='identifier', partname='rdf', data='RDF'))
        self.assertEquals(['getForApiKey', 'add'], [m.name for m in self.observer.calledMethods])
        self.assertEquals({'apiKey':'MonkeyWrench'}, self.observer.calledMethods[0].kwargs)
        self.assertEquals(dict(identifier='identifier', partname='user', data='User Name'), self.observer.calledMethods[1].kwargs)
        


