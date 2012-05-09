#!/bin/bash
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
