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

from oas.datatofield import DataToField

def lico(gen):
    return list(compose(gen))

class DataToFieldTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.data2field = DataToField(fromKwarg='data', fieldname='field')
        self.observer = CallTrace('Observer')
        self.data2field.addObserver(self.observer)

    def testAdd(self):
        lico(self.data2field.add(identifier='identifier', partname='part', data='somedata'))
        self.assertEquals(['addField'], [m.name for m in self.observer.calledMethods])
        self.assertEquals(dict(name='field', value='somedata'), self.observer.calledMethods[0].kwargs)
        
    def testAddWithoutFromKwarg(self):
        self.data2field.add(identifier='identifier', partname='part', lxmlNode='somedata')
        self.assertEquals([], [m.name for m in self.observer.calledMethods])
