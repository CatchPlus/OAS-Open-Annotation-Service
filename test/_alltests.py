#!/usr/bin/env python
from os import system                               #DO_NOT_DISTRIBUTE
from glob import glob                               #DO_NOT_DISTRIBUTE
from sys import path as systemPath                  #DO_NOT_DISTRIBUTE
system('find .. -name "*.pyc" | xargs rm -f')       #DO_NOT_DISTRIBUTE
for path in glob('../deps.d/*'):                    #DO_NOT_DISTRIBUTE
    systemPath.insert(0, path)                      #DO_NOT_DISTRIBUTE
systemPath.insert(0, '..')                          #DO_NOT_DISTRIBUTE

from unittest import main

from annotationfiltertest import AnnotationFilterTest
from utilstest import UtilsTest
from multipleannotationsplittest import MultipleAnnotationSplitTest

if __name__ == '__main__':
    main()
