#!/usr/bin/env bash

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

docker build -f Dockerfile -t "$TRAVIS_REPO_SLUG":latest .
docker push "$TRAVIS_REPO_SLUG"
