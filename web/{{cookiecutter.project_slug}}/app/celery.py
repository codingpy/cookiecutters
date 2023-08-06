from celery import Celery

app = Celery("app", broker="amqp://guest@queue//", include=["app.tasks"])
