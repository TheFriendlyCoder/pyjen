#!/bin/bash -e
export version=$1

export V1IMAGE="jenkins:1.651.3-alpine"
export V2IMAGE="jenkins:alpine"
export V1HOME=jenkins1_home
export V2HOME=jenkins2_home

if [ "$version" == "1" ]
then
    echo Running Jenkins 1 container...
    export JKIMAGE=$V1IMAGE
    export JKHOME=$V1HOME
    export JKPORT1=8081
    export JKPORT2=50001
else
    echo Running Jenkins 2 conatiner...
    export JKIMAGE=$V2IMAGE
    export JKHOME=$V2HOME
    export JKPORT1=8080
    export JKPORT2=50000
fi

[ -d $JKHOME ] || (mkdir $JKHOME && chmod a+w $JKHOME)
docker run -p $JKPORT1:8080 -p $JKPORT2:50000 -v $PWD/$JKHOME:/var/jenkins_home $JKIMAGE
#docker run -i -t -p 8080:8080 -p 50000:50000 -v $PWD/$JKHOME:/var/delme $JKIMAGE /bin/bash
#docker run -p 8080:8080 -p 50000:50000 $JKIMAGE
