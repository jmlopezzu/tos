Tasks
======

A task is a function that executes a process through multiprocessing queue.
Celery is a multiprocessing queue that handles requests and solved according
to the order of arrival of an effective way. All these functions use the
@shared_task decorator to preserve the context of Celery application that
runs on the application or Django project.
When the task contains within decorator the keyword bind equal to True,
the task can share their context in order to report on their implementation.

.. automodule:: tos_web.tasks
    :members:
    :inherited-members:
