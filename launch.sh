[ -d jenkins_home ] || mkdir jenkins_home
docker run -p 8080:8080 -p 50000:50000 -v $PWD/jenkins_home:/var/jenkins_home jenkins
