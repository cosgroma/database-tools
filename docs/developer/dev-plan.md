# Development Plan

## Command Line Design

```bash
db-man --space NOTION_OR_CONFLUENCE_URL --page-id ID
db-man --space NOTION_OR_CONFLUENCE_URL --page-title TITLE
db-man -u coverage.xml
db-man -u docs/*
db-man -u docs/* --overwrite
db-man -d docs/* --overwrite
db-man -d docs/*
db-man -s
db-man -i
db-man --init
db-man --page-id ID -d docs/*
db-man --page-title TITLE -d docs/*
db-man add-task
```

## Snippets

### Notion Objects

```python

from notion_objects import Database, Page, DynamicNotionObject
from notion_objects import *

class TitleText(Property[str]):
    type = "title"

    def get(self, field: str, obj: dict) -> str:
        items = obj["properties"][field]["title"]
        if items:
            return "".join([item["plain_text"] for item in items])
        return ""

    def set(self, field: str, value: Optional[str], obj: dict):
        # TODO: allow rich-text
        obj[field] = {
            "title": [
                {
                    "type": "text",
                    "text": {"content": value},
                    "plain_text": value,
                }
            ]
        }

class TranscriptionNotion(NotionObject):
    trans_id = TitleText("Id")
    name = Text("Name")
    created_time = CreatedTime("Created time")
    ai_summary = Text("AI summary")
    tags = MultiSelect("Tags")
    ai_keywords = MultiSelect("AI keywords")
    remove = Checkbox("Remove")
    reviewed = Status("Reviewed")
    notes = Text("Notes")



DATABASE_ID = "b754cd5cb1f4424a9ad94880df16a157"
notion = NotionClient(auth=NOTION_API_KEY)
database: Database[TranscriptionNotion] = Database(TranscriptionNotion, database_id=DATABASE_ID, client=notion)

current_properties = database.properties
for prop in current_properties:
    print(prop)

for transcription in database:
    # print(transcription.to_json())  # will print your database record as JSON
    print(f"Transcription: {transcription.trans_id} - {transcription.name[:20]} : {transcription.ai_keywords}")

def get_value(prop_type: str, value_dict: Dict[str, Any]) -> Any:
    """Get Value.

    Args:
        prop_type (str): Property Type
        value_dict ([type]): Value Dict

    Returns:
        Any: Value
    """
    if prop_type == "object":
        return get_value(value_dict[prop_type]["type"], value_dict[prop_type])

    if prop_type == "text" or prop_type == "rich_text":
        if value_dict[prop_type] is None:
            return ""
        if len(value_dict[prop_type]) == 0:
            return ""
        return value_dict[prop_type][0]["text"]["content"]
    elif prop_type == "multi_select":
        return [value["name"] for value in value_dict[prop_type]]
    elif prop_type == "title":
        return get_title_content(value_dict)
    elif prop_type == "date":
        if value_dict[prop_type] is None:
            return ""
        if "start" not in value_dict[prop_type]:
            return ""
        return value_dict[prop_type]["start"]
    elif prop_type == "checkbox":
        return value_dict[prop_type]
    elif prop_type == "number":
        return value_dict[prop_type]
    elif prop_type == "select" or prop_type == "status":
        if value_dict[prop_type] is None:
            return ""
        if "name" not in value_dict[prop_type]:
            return ""
        return value_dict[prop_type]["name"]
    elif prop_type == "people":
        return value_dict[prop_type]
    elif prop_type == "relation":
        return value_dict[prop_type]
    else:
        return value_dict[prop_type]

MIN_ATTR_LIST = ["id", "title", "created_by", "description", "properties"]
def create_dynamic_class(class_name, object_info):
    class Base:
        def __init__(self, **kwargs):
            object_type = object_info.get("type", None)
            # if object_type != "object":
            #     raise Exception(f"Invalid object type: {object_type}")
            for attr_name, details in object_info.items():
                try:
                    # print(object_info)
                    if attr_name not in MIN_ATTR_LIST:
                        # print(f"Skipping {attr_name}")
                        continue

                    if attr_name == "properties":
                        continue

                    if attr_name == "id":
                        setattr(self, attr_name, kwargs.get(attr_name, None))
                        continue

                    if isinstance(details, dict):
                        if "type" not in details:
                            continue
                        attr_type = details.get("type", None)
                        default_value = kwargs.get(attr_name, None)
                        if default_value is None:
                            print(f"missing kwargs.{attr_name}")
                        setattr(
                            self,
                            attr_name,
                            initialize_property(attr_type, default_value),
                        )

                except Exception as e:
                    raise Exception(
                        f"Error creating dynamic class: {class_name}.{attr_name} using {details} - {e}"
                    )

            properties_info = object_info.get("properties", None)
            kwargs_properties = kwargs.get("properties", None)
            for prop_name, prop_details in properties_info.items():
                # print("prop name", prop_name)
                prop_type = prop_details.get("type", None)
                default_value = kwargs_properties.get(prop_name, None)
                if default_value is None:
                    print(f"missing kwargs.{prop_name}")
                if prop_name == class_name:
                    setattr(self, "name", initialize_property(prop_type, default_value))
                    continue
                setattr(self, prop_name, initialize_property(prop_type, default_value))

        def __repr__(self):
            props_str = ", ".join(
                [f"{prop}={getattr(self, prop)}" for prop in self.__dict__]
            )
            return f"{class_name}({props_str})"

        def to_dict(self):
            return {prop: getattr(self, prop) for prop in self.__dict__}

        def from_dict(self, data):
            for prop_name, prop_details in object_info.items():
                prop_type = prop_details.get("type", None)
                default_value = data.get(prop_name, None)
                setattr(self, prop_name, initialize_property(prop_type, default_value))

    return type(class_name, (Base,), {})
```

The above code snippet demonstrates how to create a dynamic class based on the properties of a Notion object. This allows for easy manipulation of Notion objects in Python code. The `create_dynamic_class` function takes the class name and object information as input and generates a dynamic class with the specified properties. This class can then be used to interact with Notion objects and their properties. The `initialize_property` function initializes the properties of the dynamic class based on the property type and default value.

### Confluence Objects

```python
from confluence_objects import ConfluenceClient, Page, Space, Attachment

confluence = ConfluenceClient(url=CONFLUENCE_URL, username=USERNAME, password=PASSWORD)

space = Space(confluence, key="KEY")
page = Page(confluence, space=space, title="TITLE")
attachment = Attachment(confluence, page=page, file_path="FILE_PATH")

page.create()
attachment.upload()
```
