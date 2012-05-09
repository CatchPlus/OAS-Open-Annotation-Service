#!/bin/bash
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

set -e
mydir=$(cd $(dirname $0);pwd)
docdir=$mydir/doc

rm -rf tmp build

python2.6 setup.py install --root tmp --install-layout=deb
cp -r test tmp/test
cp -r doc tmp/doc
cp -r solr-data tmp/solr-data
find tmp -type f -exec sed -e \
    "/DO_NOT_DISTRIBUTE/d;
     s,binDir = '/usr/bin',binDir = '${mydir}/tmp/usr/bin',;
     s,^documentationPath.*$,documentationPath='$mydir/doc',;
     s,^usrSharePath.*$,usrSharePath='$mydir/tmp/usr/share/avarus',;" -i {} \;

export PYTHONPATH=`pwd`/tmp/usr/lib/python2.6/dist-packages:${PYTHONPATH}

teststorun=$1
if [ -z "$teststorun" ]; then
    teststorun="alltests.sh integrationtest.sh"
else
    shift
fi

echo "Will now run the tests:"
for f in $teststorun; do
    echo "- $f"
done
echo "Press [ENTER] to continue"
read

for testtorun in $teststorun; do
    (   
    cd tmp/test
    ./$testtorun "$@"
    )   
    echo "Finished $testtorun, press [ENTER] to continue"
    read
done

rm -rf tmp build
