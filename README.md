#Simple OCR SERVER

This is a simple OCR server, running a Flask server with a celery worker using ocrmypdf for OCR extracting.

To run this application just build the docker image and run:

```
docker-compose up --build
```

Follow these 2 steps to process a file.

```
#Upload a PDF to be processed and keep the task_id for tracking the process

curl -X POST \
  http://localhost:5000/upload \
  -H 'cache-control: no-cache' \
  -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
  -H 'postman-token: 1edd0112-0330-436c-435a-ca55e944880c' \
  -F 'file=@Test.pdf'

#Returns this:
{
    "task_id": "74f15b3d-a1e8-40ed-886f-b4eb07ba58cb"
}
```

```
#Request the status until it returns the state "completed" so you can download the file using the cloudinary url

curl -X GET \
  http://localhost:5000/status/74f15b3d-a1e8-40ed-886f-b4eb07ba58cb \
  -H 'cache-control: no-cache' \
  -H 'postman-token: 4c82d520-1e7d-b801-4f5c-efd168a52d52'

#Returns this:
{
    "result": {
        "data": {
            ...
            "url": "http://res.cloudinary.com/[...]/Test.pdf",
            ...
        },
        "route": "update_file",
        "task_id": "74f15b3d-a1e8-40ed-886f-b4eb07ba58cb"
    },
    "state": "completed"
}
```
