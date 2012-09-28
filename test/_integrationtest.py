# -*- coding: utf-8 -*-
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

from os import system                               #DO_NOT_DISTRIBUTE
from glob import glob                               #DO_NOT_DISTRIBUTE
from sys import path as systemPath                  #DO_NOT_DISTRIBUTE
system('find .. -name "*.pyc" | xargs rm -f')       #DO_NOT_DISTRIBUTE
for path in glob('../deps.d/*'):                    #DO_NOT_DISTRIBUTE
    systemPath.insert(0, path)                      #DO_NOT_DISTRIBUTE
systemPath.insert(0, '..')                          #DO_NOT_DISTRIBUTE

from sys import argv

from seecr.test.testrunner import TestRunner
from integration import OasIntegrationState

flags = ['--fast']

if __name__ == '__main__':
    fastMode = '--fast' in argv
    for flag in flags:
        if flag in argv:
            argv.remove(flag)

    groupnames = None
    if '--group' in argv:
        pos = argv.index('--group')
        groupnames = [argv[pos+1]]
        del argv[pos:pos+2]

    runner = TestRunner()
    OasIntegrationState(
        'default', 
        tests=[
            'integration.oastest.OasTest',
            'integration.usertest.UserTest',
        ],
        fastMode=fastMode).addToTestRunner(runner)
    OasIntegrationState(
        'initial', 
        tests=[
            'integration.initialtest.InitialTest',
        ],
        fastMode=fastMode).addToTestRunner(runner)
    OasIntegrationState(
        'resolve', 
        tests=[
            'integration.resolvetest.ResolveTest',
        ],
        fastMode=fastMode).addToTestRunner(runner)
    OasIntegrationState(
        'harvester', 
        tests=[
            'integration.harvestertest.HarvesterTest',
        ],
        fastMode=fastMode).addToTestRunner(runner)
    OasIntegrationState(
        'constraints', 
        tests=[
            'integration.constraintstest.ConstraintsTest',
            'integration.inlinetest.InlineTest',
        ],
        fastMode=fastMode).addToTestRunner(runner)
    OasIntegrationState(
        'constrains_body', 
        tests=[
            'integration.constrainsbodytest.ConstrainsBodyTest',
        ],
        fastMode=fastMode).addToTestRunner(runner)

    testnames = argv[1:]
    if groupnames is None:
        runner.run(testnames)
    else:
        runner.run(testnames, groupnames=groupnames)

