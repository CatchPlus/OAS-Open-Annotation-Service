# -*- coding: utf-8 -*-

from os import system                               #DO_NOT_DISTRIBUTE
from glob import glob                               #DO_NOT_DISTRIBUTE
from sys import path as systemPath                  #DO_NOT_DISTRIBUTE
system('find .. -name "*.pyc" | xargs rm -f')       #DO_NOT_DISTRIBUTE
for path in glob('../deps.d/*'):                    #DO_NOT_DISTRIBUTE
    systemPath.insert(0, path)                      #DO_NOT_DISTRIBUTE
systemPath.insert(0, '..')                          #DO_NOT_DISTRIBUTE

from sys import argv

from testrunner import TestRunner

from integration import globalSetUp, globalTearDown

flags = ['--fast']

if __name__ == '__main__':
    fastMode = '--fast' in argv
    for flag in flags:
        if flag in argv:
            argv.remove(flag)

    runner = TestRunner()
    runner.addGroup(
        'default', [
            'integration.oastest.OasTest',
        ],
        groupSetUp = lambda: globalSetUp(fastMode, 'default'),
        groupTearDown = lambda: globalTearDown()
    )
    runner.addGroup(
        'initial', [
            'integration.initialtest.InitialTest',
        ],
        groupSetUp = lambda: globalSetUp(fastMode, 'initial'),
        groupTearDown = lambda: globalTearDown()
    )
    runner.addGroup(
        'resolve', [
            'integration.resolvetest.ResolveTest',
        ],
        groupSetUp = lambda: globalSetUp(fastMode, 'resolve'),
        groupTearDown = lambda: globalTearDown()
    )

    testnames = argv[1:]
    runner.run(testnames)
    
