#Simple OCR SERVER

<img align="right" height="200" src="https://raw.githubusercontent.com/psleo/python-ocr-server/master/python-ocr-server.png">

This is a simple OCR server, running a Flask server with a celery worker using ocrmypdf for OCR extracting.

To run this application, configure your cloudinary credentials on 'app.py' and build the docker image and run:

```
docker-compose up --build
```

<p align="center">
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT Licensed" />
  </a>
</p>


Follow these 2 steps to process a file.

```
#Upload a PDF to be processed and keep the task_id for tracking the process

curl -X POST \
  http://localhost:5000/upload \
  -H 'cache-control: no-cache' \
  -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
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
  -H 'cache-control: no-cache'

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

---

#Creating a server:
https://nickjanetakis.com/blog/dockerize-a-flask-celery-and-redis-application-with-docker-compose

#Sample repository:
https://github.com/nickjj/build-a-saas-app-with-flask/

#OCR:
https://ocrmypdf.readthedocs.io/en/latest/cookbook.html

#Reference
https://github.com/miguelgrinberg ( Miguel Grinberg )

---

