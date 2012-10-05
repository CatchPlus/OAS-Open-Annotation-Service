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


function message {
    echo "
$1" | sed 's/^/* /'
}

function messageWithEnter {
    message "$1"
    read -p "Press [ENTER] to continue"
}

function isroot {
    if [ "$(id -u)" != "0" ]
    then
        message "Need to be root"
        exit -1
    fi
}

USERINPUT=""

function show_question {
    USERINPUT=""

    local question="$1"
    if [ "$2" != "" ]; then
        question="$question [$2]:"
    else
        question="$question "
    fi

    read -p "$question" USERINPUT
    if [ "$USERINPUT" == "" ]; then
        USERINPUT=$2
    fi
}

function ask_question {
    question=$1
    default=$2

    valid=""
    if [ $# -ge 3 ]; then
        shift 2
        valid=$@
        question="$question ($(echo $valid | tr ' ' '/'))"
    fi

    question_answered="N"
    while [ $question_answered == "N" ]
    do
        show_question "$question" "$default"
        if [ "$valid" != "" ]; then
            for v in $valid; do
                if [ "$v" == "$USERINPUT" ]; then
                    question_answered="Y"
                fi
            done
        else
            question_answered="Y"
        fi
    done
}

function create_user {
    username=$1
    if [ ! -d /home/$username ]
    then
        message "Creating '$username'"
        useradd --create-home $username --shell /bin/bash
    fi
    sshdir=/home/$username/.ssh
    authorizedKeysFile=$sshdir/authorized_keys
    if [ ! -f $authorizedKeysFile ]; then
        test -d $sshdir || mkdir $sshdir
        cp /root/.ssh/authorized_keys ${authorizedKeysFile}
        chown $username:$username $sshdir -R
    fi
}

function checkoutGit {
    username=$1
    destdir=$2
    giturl=$3
    version=$4
    if [ ! -d $destdir ]; then
        git clone $giturl $destdir
    fi
    if [ "$version" == "master" ]; then
    (   cd $destdir
        git checkout master
        git pull
    )
    else
    (
        cd $destdir
        git fetch
        currentbranch="$(git branch --no-color |\
            sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/')"
        newbranch="version/$version"
        if [ "$currentbranch" != "$newbranch" ]; then
            git checkout -b "$newbranch" $version
        else
            echo "Git already on branch '$newbranch'"
        fi
    )
    fi
   
    if [ $? -ne 0 ]; then 
        exit 1
    fi
    chown $username:$username $destdir -R
}

function checkoutSvn {
    username=$1
    destdir=$2
    svnurl=$3
    shift 3
    svnparams="$@"
    if [ ! -d $destdir ]; then
        svn co $svnparams $svnurl $destdir
    else
        (
            cd $destdir
            svn switch $svnparams $svnurl
        )
    fi
    chown $username:$username $destdir -R
}

PORTSCONF=/etc/apache2/ports.conf
function removeListenLine {
    port=$1

    oldconfig=$(cat $PORTSCONF | grep -v "^\s*Listen\\W*$port\$" | cat -)
    echo "$oldconfig" > $PORTSCONF
}

function addListenLine {
    port=$1
    removeListenLine $port

    echo "Listen $port" >> $PORTSCONF
}

function removeNameVirtualHost {
    port=$1

    oldconfig=$(cat $PORTSCONF | grep -v "^NameVirtualHost\\W*.*\:$port\$" | cat -)
    echo "$oldconfig" > $PORTSCONF
}

function stopService {
    local SERVICE_NAME=$1
    if [ -e "/etc/service/$SERVICE_NAME" ]; then
        (
            cd /etc/service/$SERVICE_NAME
            rm /etc/service/$SERVICE_NAME
            svc -dx . log
        )
    fi
}

function createService {
    local USERNAME=$1
    local GROUPNAME=$2
    local SERVICEDIR=$3
    local SERVICE_NAME=$4
    local SCRIPTBODY=$5

    stopService ${SERVICE_NAME}

    test -d $SERVICEDIR/$SERVICE_NAME && mv $SERVICEDIR/$SERVICE_NAME $SERVICEDIR/$SERVICE_NAME.tmp
    mkdir --parents $SERVICEDIR/$SERVICE_NAME/log/main
    chown ${USERNAME}:${GROUPNAME} $SERVICEDIR/$SERVICE_NAME/log/main

    echo "#!/bin/bash

exec /usr/bin/setuidgid $USERNAME /usr/bin/multilog t n50 s9999999 ./main 2>&1
    " > $SERVICEDIR/$SERVICE_NAME/log/run
    chmod +x $SERVICEDIR/$SERVICE_NAME/log/run

    echo "#!/bin/bash

export LANG=en_US.UTF-8
$SCRIPTBODY
" > $SERVICEDIR/$SERVICE_NAME/run
    chmod +x $SERVICEDIR/$SERVICE_NAME/run
    touch $SERVICEDIR/$SERVICE_NAME/down
    
    rm -rf $SERVICEDIR/$SERVICE_NAME.tmp
}

function startService {
    local SERVICEDIR=$1
    local SERVICE_NAME=$2
    (
        cd /etc/service
        rm $SERVICEDIR/$SERVICE_NAME/down 
        ln -s $SERVICEDIR/$SERVICE_NAME $SERVICE_NAME
    )
}

function prepareService {
    local SERVICEDIR=$1
    local SERVICE_NAME=$2
    (
        cd /etc/service
        ln -s $SERVICEDIR/$SERVICE_NAME $SERVICE_NAME
    )
    message "Service $SERVICE_NAME created, not yet started.

To start:
rm /etc/service/$SERVICE_NAME/down; svc -u /etc/service/$SERVICE_NAME"
}

function prepareAndStartService {
    local SERVICEDIR=$1
    local SERVICE_NAME=$2
    (
        cd /etc/service
        rm $SERVICEDIR/$SERVICE_NAME/down
        ln -s $SERVICEDIR/$SERVICE_NAME $SERVICE_NAME
    )
    message "Service $SERVICE_NAME started."
}

function sectionInFile {
    FILENAME=$1
    CONTENT=$2

    if [ ! -f $FILENAME ]; then
        touch $FILENAME
    fi
    
    FILTERED=$(cat ${FILENAME} | awk '
    BEGIN { passthrough=1 } 
    { if ($0 == "## START CQ2") {
        passthrough=0
      }; 
      if ($0 == "## END CQ2") {
        passthrough=1
      } else { 
        if (passthrough == 1) {
          print $0
        }
      };
    }')

    echo "${FILTERED}
## START CQ2
${CONTENT}
## END CQ2
" > ${FILENAME}

}
