#!/bin/bash -e
export version=$1

export V1IMAGE="jenkins:1.651.3"
export V2IMAGE="jenkins:latest"
export V1HOME=jenkins1_home
export V2HOME=jenkins2_home

if [ "$version" == "1" ]
then
    export IMAGE=$V1IMAGE
    export HOME=$V1HOME
else
    export IMAGE=$V2IMAGE
    export HOME=$V2HOME
fi

echo Home is $HOME
echo Image is $IMAGE
exit

[ -d jenkins_home ] || (mkdir jenkins_home && sudo chown 1000 jenkins_home)
docker run -p 8080:8080 -p 50000:50000 -v $PWD/jenkins_home:/var/jenkins2_home $V1IMAGE
