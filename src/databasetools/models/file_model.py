from typing import Optional

from pydantic import BaseModel


class FileMetadata(BaseModel):
    conversation_id: str
    title: str
    snippet: str
    processed_time: float
    file_name: str
    project: Optional[str] = None


# {
# "object": "page",
# "id": "44a057c1ee38483b8d88c9a5e6d3dce2",
# "created_time": "2024-04-27T20:33:00.000Z",
# "last_edited_time": "2024-05-12T21:08:00Z",
# "created_by": {
#     "object": "user",
#     "id": "d870b97f-82c7-4813-b9e3-7c87e5d4ad72"
# },
# "last_edited_by": {
#     "object": "user",
#     "id": "e10ec689-0d5a-463f-b9e8-03d1cf55f4f1"
# },
# "cover": null,
# "icon": null,
# "parent": {
#     "type": "workspace",
#     "workspace": true
# },
# "archived": false,
# "in_trash": false,
# "properties": {
#     "title": {
#         "id": "title",
#         "type": "title",
#         "title": [
#             {
#                 "type": "text",
#                 "text": {
#                     "content": "Integration Test Area",
#                     "link": null
#                 },
#                 "annotations": {
#                     "bold": false,
#                     "italic": false,
#                     "strikethrough": false,
#                     "underline": false,
#                     "code": false,
#                     "color": "default"
#                 },
#                 "plain_text": "Integration Test Area",
#                 "href": null
#             }
#         ]
#     }
# },
# "url": "https://www.notion.so/Integration-Test-Area-44a057c1ee38483b8d88c9a5e6d3dce2",
# "public_url": null,
# "request_id": "af7ff79c-836e-457b-8e5e-29b5288e7147"
# }

# {
#     "generated_": {
#         "id": "CGUn",
#         "name": "generated_",
#         "type": "unique_id",
#         "unique_id": {
#             "prefix": "M4T"
#         }
#     },
#     "Created time": {
#         "id": "EEuz",
#         "name": "Created time",
#         "type": "created_time",
#         "created_time": {}
#     },
#     "File Path": {
#         "id": "NF%5Ch",
#         "name": "File Path",
#         "type": "rich_text",
#         "rich_text": {}
#     },
#     "Processed": {
#         "id": "O%5DS%5D",
#         "name": "Processed",
#         "type": "checkbox",
#         "checkbox": {}
#     },
#     "Length Seconds": {
#         "id": "P%5Bqr",
#         "name": "Length Seconds",
#         "type": "number",
#         "number": {
#             "format": "number"
#         }
#     },
#     "Tags": {
#         "id": "Y%3C%3CX",
#         "name": "Tags",
#         "type": "multi_select",
#         "multi_select": {
#             "options": [
#                 {
#                     "id": "fef4d5ce-973f-4368-9904-18ae2489a8db",
#                     "name": "Test",
#                     "color": "brown",
#                     "description": null
#                 },
#                 {
#                     "id": "a7a74510-3da1-49bb-b510-b5375deaf391",
#                     "name": "Task",
#                     "color": "orange",
#                     "description": null
#                 },
#                 {
#                     "id": "167a9e75-108d-4ffd-ac80-32b21546b88e",
#                     "name": "Tags",
#                     "color": "blue",
#                     "description": null
#                 }
#             ]
#         }
#     },
#     "Size Bytes": {
#         "id": "YNlR",
#         "name": "Size Bytes",
#         "type": "number",
#         "number": {
#             "format": "number"
#         }
#     },
#     "Upload Date": {
#         "id": "h%5B%3Ff",
#         "name": "Upload Date",
#         "type": "date",
#         "date": {}
#     },
#     "Status": {
#         "id": "imf%7B",
#         "name": "Status",
#         "type": "status",
#         "status": {
#             "options": [
#                 {
#                     "id": "b336d2ca-92f9-4386-9785-bb6b5c0d630d",
#                     "name": "Not started",
#                     "color": "default",
#                     "description": null
#                 },
#                 {
#                     "id": "3e6623d1-d5bc-46ef-a3b8-b8dc6ec18117",
#                     "name": "In progress",
#                     "color": "blue",
#                     "description": null
#                 },
#                 {
#                     "id": "3ffa976d-2477-4dcd-95d2-cf664331ed92",
#                     "name": "Done",
#                     "color": "green",
#                     "description": null
#                 }
#             ],
#             "groups": [
#                 {
#                     "id": "cd3392b5-0c0f-4b57-8b27-607229e12e75",
#                     "name": "To-do",
#                     "color": "gray",
#                     "option_ids": [
#                         "b336d2ca-92f9-4386-9785-bb6b5c0d630d"
#                     ]
#                 },
#                 {
#                     "id": "014be9e1-97a6-4def-b2fe-bbc8225d5116",
#                     "name": "In progress",
#                     "color": "blue",
#                     "option_ids": [
#                         "3e6623d1-d5bc-46ef-a3b8-b8dc6ec18117"
#                     ]
#                 },
#                 {
#                     "id": "d3266a76-615e-4109-8829-7a891a00833b",
#                     "name": "Complete",
#                     "color": "green",
#                     "option_ids": [
#                         "3ffa976d-2477-4dcd-95d2-cf664331ed92"
#                     ]
#                 }
#             ]
#         }
#     },
#     "Is Active": {
#         "id": "lVGp",
#         "name": "Is Active",
#         "type": "checkbox",
#         "checkbox": {}
#     },
#     "Ref": {
#         "id": "title",
#         "name": "Ref",
#         "type": "title",
#         "title": {}
#     }
# }

# {
#         "object": "page",
#         "id": "3f26897e41ad404ebb68e0b2768fc602",
#         "created_time": "2024-05-12T21:37:00.000Z",
#         "last_edited_time": "2024-05-12T21:37:00Z",
#         "created_by": {
#             "object": "user",
#             "id": "e10ec689-0d5a-463f-b9e8-03d1cf55f4f1"
#         },
#         "last_edited_by": {
#             "object": "user",
#             "id": "e10ec689-0d5a-463f-b9e8-03d1cf55f4f1"
#         },
#         "cover": null,
#         "icon": null,
#         "parent": {
#             "type": "database_id",
#             "database_id": "62c81d1f-eaaf-4852-88b4-758ec7516b89"
#         },
#         "archived": false,
#         "in_trash": false,
#         "properties": {
#             "generated_": {
#                 "id": "CGUn",
#                 "type": "unique_id",
#                 "unique_id": {
#                     "prefix": "M4T",
#                     "number": 79
#                 }
#             },
#             "Created time": {
#                 "id": "EEuz",
#                 "type": "created_time",
#                 "created_time": "2024-05-12T21:37:00.000Z"
#             },
#             "File Path": {
#                 "id": "NF%5Ch",
#                 "type": "rich_text",
#                 "rich_text": [
#                     {
#                         "type": "text",
#                         "text": {
#                             "content": "C:\\Users\\cosgroma\\AppData\\Roaming\\EchoScribe\\recordings\\R2023-09-20-06-35-47.WAV",
#                             "link": null
#                         },
#                         "annotations": {
#                             "bold": false,
#                             "italic": false,
#                             "strikethrough": false,
#                             "underline": false,
#                             "code": false,
#                             "color": "default"
#                         },
#                         "plain_text": "C:\\Users\\cosgroma\\AppData\\Roaming\\EchoScribe\\recordings\\R2023-09-20-06-35-47.WAV",
#                         "href": null
#                     }
#                 ]
#             },
#             "Processed": {
#                 "id": "O%5DS%5D",
#                 "type": "checkbox",
#                 "checkbox": true
#             },
#             "Length Seconds": {
#                 "id": "P%5Bqr",
#                 "type": "number",
#                 "number": 0
#             },
#             "Tags": {
#                 "id": "Y%3C%3CX",
#                 "type": "multi_select",
#                 "multi_select": []
#             },
#             "Size Bytes": {
#                 "id": "YNlR",
#                 "type": "number",
#                 "number": 51165696
#             },
#             "Upload Date": {
#                 "id": "h%5B%3Ff",
#                 "type": "date",
#                 "date": {
#                     "start": "2024-03-29",
#                     "end": null,
#                     "time_zone": null
#                 }
#             },
#             "Status": {
#                 "id": "imf%7B",
#                 "type": "status",
#                 "status": {
#                     "id": "b336d2ca-92f9-4386-9785-bb6b5c0d630d",
#                     "name": "Not started",
#                     "color": "default"
#                 }
#             },
#             "Is Active": {
#                 "id": "lVGp",
#                 "type": "checkbox",
#                 "checkbox": false
#             },
#             "Ref": {
#                 "id": "title",
#                 "type": "title",
#                 "title": [
#                     {
#                         "type": "text",
#                         "text": {
#                             "content": "136779d9-2cdc-489b-b444-c128550f81ab",
#                             "link": null
#                         },
#                         "annotations": {
#                             "bold": false,
#                             "italic": false,
#                             "strikethrough": false,
#                             "underline": false,
#                             "code": false,
#                             "color": "default"
#                         },
#                         "plain_text": "136779d9-2cdc-489b-b444-c128550f81ab",
#                         "href": null
#                     }
#                 ]
#             }
#         },
#         "url": "https://www.notion.so/136779d9-2cdc-489b-b444-c128550f81ab-3f26897e41ad404ebb68e0b2768fc602",
#         "public_url": null,
#         "request_id": "95426e40-d033-4f69-9de1-23f53bca5dce"
#     },
# "object": "block",
# "id": "62c81d1feaaf485288b4758ec7516b89",
# "parent": {
#     "type": "page_id",
#     "page_id": "44a057c1-ee38-483b-8d88-c9a5e6d3dce2"
# },
# "created_time": "2024-04-27T22:44:00.000Z",
# "last_edited_time": "2024-05-04T23:02:00Z",
# "created_by": {
#     "object": "user",
#     "id": "d870b97f-82c7-4813-b9e3-7c87e5d4ad72"
# },
# "last_edited_by": {
#     "object": "user",
#     "id": "d870b97f-82c7-4813-b9e3-7c87e5d4ad72"
# },
# "has_children": false,
# "archived": false,
# "in_trash": false,
# "type": "child_database",
# "child_database": {
#     "title": "TestDatabase"
# },
# "children": []
