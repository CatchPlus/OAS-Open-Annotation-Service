#!/usr/bin/env python
from os import system                               #DO_NOT_DISTRIBUTE
from glob import glob                               #DO_NOT_DISTRIBUTE
from sys import path as systemPath                  #DO_NOT_DISTRIBUTE
system('find .. -name "*.pyc" | xargs rm -f')       #DO_NOT_DISTRIBUTE
for path in glob('../deps.d/*'):                    #DO_NOT_DISTRIBUTE
    systemPath.insert(0, path)                      #DO_NOT_DISTRIBUTE
systemPath.insert(0, '..')                          #DO_NOT_DISTRIBUTE

from unittest import main

from apikeytest import ApiKeyTest
from apikeychecktest import ApiKeyCheckTest
from authorizationtest import AuthorizationTest
from deanonymizetest import DeanonymizeTest
from identifierfromxpathtest import IdentifierFromXPathTest
from multipleannotationsplittest import MultipleAnnotationSplitTest
from normalizetest import NormalizeTest
from publishtest import PublishTest
from rdfcontainertest import RdfContainerTest
from resolveservertest import ResolveServerTest
from utilstest import UtilsTest

from login.passwordfiletest import PasswordFileTest
from login.basichtmlloginformtest import BasicHtmlLoginFormTest

if __name__ == '__main__':
    main()
