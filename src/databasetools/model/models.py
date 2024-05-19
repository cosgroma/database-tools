from notion_objects import Page
from notion_objects.properties import Status
from notion_objects.properties import TitleText
from pydantic import BaseModel


class SimpleTask(BaseModel):
    name: str
    status: str


class Task(Page):
    name = TitleText("Name")
    status = Status("Status")

    def to_simple_task(self) -> SimpleTask:
        return SimpleTask(name=self.name, status=self.status)


# Usage
task = Task(name="Task Name", status="Incomplete")
simple_task = task.to_simple_task()
print(simple_task.model_dump_json())
