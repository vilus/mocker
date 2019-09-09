# http mock server

[![Build Status](https://travis-ci.org/vilus/mocker.svg?branch=master)](https://travis-ci.org/vilus/mocker)
[![codecov](https://codecov.io/gh/vilus/mocker/branch/master/graph/badge.svg)](https://codecov.io/gh/vilus/mocker)

Returns http responses by matching requests.

Request matching defined by: `host` `method` `path` (its can be any - `*`)

Responses defined by: `message body` `status_code` `headers`

_term_ `mock` is request matching + responses

Mock created via http POST request to `/mocker_api/mocks/` (examples below)

At the same time can be created several "similar" mocks (equivalent request matching and equals responses) if no one is exclusive

When creates "overlap" mocks (equivalent request matching but different responses) then server returns http 409 status code 

About mock:
- has timeout (ttl)
- has response type 
  - single (default): `A` -> `A` `A` `A`,
  - sequence: [`A`, `B`, `C`] -> `A` `B` `C` `C` `C` ...
  - cycle: [`A`, `B`, `C`] -> `A` `B` `C` `A` `B` `C` ...
- can be exclusive (no other similar mocks might be created, False by default)

Mock deleted via http DELETE request to `/mocker_api/mocks/<pk>/`
(response has json with key `is_expired`)

Mocks CRUD also available via browser (Django REST framework builtin UI)

Examples:
- create mocks:
```bash
curl -H "Content-Type: application/json" -X POST -d '{"method":"GET","route":"/42","responses":42, "is_exclusive": true}' srv:8080/mocker_api/mocks/
{"url":"http://srv:8080/mocker_api/mocks/2/","name":"*","created":"2019-09-03T11:16:04.161986Z","expired":"2019-09-03T11:18:04.161853Z","ttl":120,"is_exclusive":false,"host":"*","route":"/42","method":"GET","responses":42,"response_type":"single"}
```

```bash
curl -H "Content-Type: application/json" -X POST -d '{"name":"all_match_cycle","host":"*","method":"*","route":"*","ttl":600,"responses":[{"body": "qwerty", "return_code": 201}, 42, {"body": "hello world", "headers":{"Content-Type": "application/json"}}], "response_type": "cycle"}' srv:8080/mocker_api/mocks/
{"url":"http://srv:8080/mocker_api/mocks/3/", "name":"all_match_cycle", ...
```

- responses:
```bash
curl -i -X POST srv:8080/some_path
HTTP/1.1 201 Created
Content-Type: text/html; charset=utf-8

qwerty
```

```bash
curl -i -X GET srv:8080/
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

42
```

```bash
curl -i -X PUT srv:8080/some_other_path
HTTP/1.1 200 OK
Content-Type: application/json

hello world
```

- show mocks:
```bash
curl -X GET srv:8080/mocker_api/mocks/
```


- delete mock:
```bash
curl -X DELETE srv:8080/mocker_api/mocks/2/
{"is_expired":true}
```

```bash
curl -X DELETE srv:8080/mocker_api/mocks/3/
{"is_expired":false}
```

other examples in tests


**Install**

for example via docker-compose:
```bash
docker-compose -f docker-compose.yml -f docker-compose.stage.yml up -d
docker-compose -f docker-compose.yml -f docker-compose.stage.yml run --rm --no-deps --entrypoint "" srv pytest
```
or any other way 