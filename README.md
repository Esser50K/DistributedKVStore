# Distributed key value store

Simple webserver exposing a key value datastore api

## Usage

To write to the store simply make a POST request with the contents in json format
```
curl -X POST http://localhost:8080/set -H 'Content-Type: application/json' -d '{"hello": "world", "nice": "to meet you"}'
```

To retrieve data from the store simply make a GET request specifying which keys are of interest (if keys are not found they'll simply not be in the response)
```
curl http://localhost:8080/get?keys=hello,nice
```

To delete a keys that was written one can send a DELETE request to the root path (the result will be a list with all the deleted keys)
```
curl -X DELETE http://localhost:8080?keys=hello,nice
```

## Build

The server is meant to be built and run with Docker but can be done locally.

Locally just make sure to install all dependencies with:
```
pip3 install -r requirements.txt
```

To build it with Docker use:
```
docker build -t store .
```

## Deployment

To run the server locally one can simply run:
```
python3 main.py
```

Or using Docker with:
```
docker run -it -p8080:8080 -v ./data:/data -e PERSIST_DIR=/data store
```