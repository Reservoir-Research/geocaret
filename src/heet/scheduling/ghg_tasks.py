"""Module with tasks specific to GHG emission calculations."""
from tasks import Executable, LocalTask, WebTask, GoogleTask, TaskLevel
from heet.events.event_handler import EventHandler

# Prepare greet task
greet_task = LocalTask(
    model=Executable(fun=print("hello"), fail_out=1, success_out=None),
    event_handler=EventHandler(),
    tak_level=TaskLevel.NOTCRITICAL)

if __name__ == '__main__':
    greet_task.run()
