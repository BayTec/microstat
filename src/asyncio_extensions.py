from asyncio import Task, create_task, CancelledError, Event

class Subscription:
    task: Task

    def __init__(self, task: Task) -> None:
        self.task = task
        pass

    def cancel(self) -> None: 
        self.task.cancel()
    
def subscribe_event(event: Event, listener) -> Subscription:
    async def listen():
        try: 
            while True:
                event.clear()
                await event.wait()
                listener()
        except CancelledError: 
            pass

    task = create_task(listen())
    return Subscription(task)