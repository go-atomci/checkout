# git-checkout

## Overview

## ChangeLog

### `v1`

#### how to use

- a. build/run docker

    ```sh
    docker build -t colynn/gitchekcout:v1 .
    docker run --rm -it colynn/git-checkout:v1 /bin/sh
    ```

- b. then run commands as below in the container

    ```sh
    export JENKINS_SLAVE_WORKSPACE=/home/jenkins/agent  #自定义目录
    export REPO_CNF='{"github.com":["oauth2",""]}'  #repo auth info
    checkout.py  --project-id 3 --stage-id 3 --publish-job-id 17  --scm-app-id 3 --app-name golang-app-demo --branch-url https://github.com/go-atomci/golang-app-demo.git --vcs-type git --build-path /  --branch-name main
    ```
