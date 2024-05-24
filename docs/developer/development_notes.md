# Development Notes

## Testing

Testing your features is crucial to ensure that your ChatManager class works correctly. Using a test database is a good idea because it allows you to keep the collection names the same as in production while isolating your test data.

Here's a general approach to setting up and testing your features:

1. **Create a Test Database**: You can create a separate database specifically for testing. This way, you can use the same collection names as production without affecting your production data.
2. **Use a Testing Framework**: Use a Python testing framework like **`unittest`** or **`pytest`** to write and run your tests.
3. **Mocking MongoDB Operations**: For some tests, especially unit tests, you can use libraries like **`mongomock`** to mock MongoDB operations. This allows you to test without needing a real MongoDB instance.

Here's how you can set up and test your ChatManager class:

### **Setting Up the Test Database**

First, ensure you have a separate test database in your MongoDB server. You can name it something like **`chatgpt_db_test`**.

### **Writing Tests**

Here's an example using **`unittest`** and **`mongomock`** to mock MongoDB operations:

```python
import unittest
from unittest.mock import patch, MagicMock
import mongomock
from chat_manager import ChatManager  # Assuming your class is in chat_manager.py

class TestChatManager(unittest.TestCase):
    @patch('pymongo.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        # Setup a test instance of ChatManager with the mock client
        self.manager = ChatManager(
            db_uri="mongodb://localhost:27017",
            db_name="chatgpt_db_test",
            username="root",
            password="example"
        )
        self.test_conversation = {
            'id': 'conv1',
            'title': 'Test Conversation',
            'create_time': 1622559600,
            'update_time': 1622559600,
            'mapping': {
                'map1': {
                    'id': 'map1',
                    'parent': None,
                    'children': [],
                    'message': {
                        'id': 'msg1',
                        'create_time': 1622559600,
                        'update_time': 1622559600,
                        'status': 'sent',
                        'end_turn': False,
                        'metadata': {},
                        'recipient': 'user',
                        'author': {'role': 'user'},
                        'content': {
                            'parts': [{'text': 'Hello!'}]
                        }
                    }
                }
            }
        }

    def test_get_content(self):
        message = self.test_conversation['mapping']['map1']['message']
        content = self.manager.get_content(message)
        self.assertEqual(content['role'], 'user')
        self.assertEqual(content['content'], 'Hello!')

    def test_upload_to_mongo(self):
        self.manager.upload_to_mongo([self.test_conversation])
        result = self.manager.conversations_collection.find_one({'id': 'conv1'})
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Test Conversation')

    def test_process_conversation(self):
        processed = self.manager.process_conversation(self.test_conversation)
        self.assertIn('message_set', processed)
        self.assertEqual(len(processed['message_set']), 1)
        self.assertEqual(processed['message_set'][0]['content'], 'Hello!')

    def tearDown(self):
        # Clear the test database after each test
        self.manager.conversations_collection.drop()

if __name__ == '__main__':
    unittest.main()

```

### **Running the Tests**

To run the tests, simply execute the test script. If you're using a file named **`test_chat_manager.py`**, you can run it using:

```sh
python -m unittest test_chat_manager.py

```

### **Notes**

- **Mocking MongoDB Operations**: Using **`mongomock`** allows you to run tests without a real MongoDB instance. This is useful for unit tests but doesn't replace integration tests with a real database.
- **Integration Tests**: For integration tests, use a real MongoDB instance with a separate test database. This ensures your code works correctly in an environment similar to production.
- **Cleaning Up**: Ensure you clean up the test database after each test run to avoid stale data affecting your tests.

### **Testing Title Extraction**

You can add a test to ensure the title extraction works correctly:

```python
import unittest
from unittest.mock import patch, MagicMock
import mongomock
from chat_manager import ChatManager  # Assuming your class is in chat_manager.py

class TestChatManager(unittest.TestCase):
    @patch('pymongo.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        # Setup a test instance of ChatManager with the mock client
        self.manager = ChatManager(
            db_uri="mongodb://localhost:27017",
            db_name="chatgpt_db_test",
            username="root",
            password="example"
        )
        self.test_conversation = {
            'id': 'conv1',
            'title': 'Test Conversation',
            'create_time': 1622559600,
            'update_time': 1622559600,
            'mapping': {
                'map1': {
                    'id': 'map1',
                    'parent': None,
                    'children': [],
                    'message': {
                        'id': 'msg1',
                        'create_time': 1622559600,
                        'update_time': 1622559600,
                        'status': 'sent',
                        'end_turn': False,
                        'metadata': {},
                        'recipient': 'user',
                        'author': {'role': 'user'},
                        'content': {
                            'parts': [{'text': 'Hello!'}]
                        }
                    }
                }
            }
        }

    def test_get_content(self):
        message = self.test_conversation['mapping']['map1']['message']
        content = self.manager.get_content(message)
        self.assertEqual(content['role'], 'user')
        self.assertEqual(content['content'], 'Hello!')

    def test_upload_to_mongo(self):
        self.manager.upload_to_mongo([self.test_conversation])
        result = self.manager.conversations_collection.find_one({'id': 'conv1'})
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Test Conversation')

    def test_process_conversation(self):
        processed = self.manager.process_conversation(self.test_conversation)
        self.assertIn('message_set', processed)
        self.assertEqual(len(processed['message_set']), 1)
        self.assertEqual(processed['message_set'][0]['content'], 'Hello!')

    def test_conversation_title(self):
        title = self.test_conversation['title']
        self.assertEqual(title, 'Test Conversation')

    def tearDown(self):
        # Clear the test database after each test
        self.manager.conversations_collection.drop()

if __name__ == '__main__':
    unittest.main()

```

This test suite includes a specific test for the conversation title to ensure it's correctly extracted from the JSON data. This should help you validate that your title extraction logic works as expected.


### **Running Tests with Pydantic**

You can also use Pydantic models in your tests to ensure your data conforms to the expected structure:

```python
import unittest
from unittest.mock import patch
import mongomock
from chat_manager import ChatManager, Conversation, Message, Mapping, MessageContent, Author

class TestChatManager(unittest.TestCase):
    @patch('pymongo.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        # Setup a test instance of ChatManager with the mock client
        self.manager = ChatManager(
            db_uri="mongodb://localhost:27017",
            db_name="chatgpt_db_test",
            username="root",
            password="example"
        )
        self.test_conversation = Conversation(
            id='conv1',
            conversation_id='conv1',
            conversation_template_id='template1',
            gizmo_id='gizmo1',
            title='Test Conversation',
            create_time=1622559600,
            update_time=1622559600,
            mapping={
                'map1': Mapping(
                    id='map1',
                    parent=None,
                    children=[],
                    message=Message(
                        id='msg1',
                        create_time=1622559600,
                        update_time=1622559600,
                        status='sent',
                        end_turn=False,
                        metadata={},
                        recipient='user',
                        author=Author(role='user'),
                        content=MessageContent(parts=[{'text': 'Hello!'}])
                    )
                )
            },
            moderation_results=[],
            current_node='node1',
            plugin_ids=[]
        )

    def test_get_content(self):
        message = self.test_conversation.mapping['map1'].message
        content = self.manager.get_content(message)
        self.assertEqual(content['role'], 'user')
        self.assertEqual(content['content'], 'Hello!')

    def test_upload_to_mongo(self):
        self.manager.upload_to_mongo([self.test_conversation])
        result = self.manager.conversations_collection.find_one({'id': 'conv1'})
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Test Conversation')

    def test_process_conversation(self):
        processed = self.manager.process_conversation(self.test_conversation)
        self.assertIn('message_set', processed.dict())
        self.assertEqual(len(processed.message_set), 1)
        self.assertEqual(processed.message_set[0]['content'], 'Hello!')

    def test_conversation_title(self):
        title = self.test_conversation.title
        self.assertEqual(title, 'Test Conversation')

    def tearDown(self):
        # Clear the test database after each test
        self.manager.conversations_collection.drop()

if __name__ == '__main__':
    unittest.main()

```

This setup allows you to define a clear, consistent schema for your data and ensure it's validated and processed correctly.

## Watcher for MongoDB Collection Changes

*What if I wanted to have something that could watch for changes at a Mongo database for particular collection names?*

*And if any new entries had been added, that that would trigger procedures that could run, and that there would be a way that I could register additional features that would enable the processing of these conversations to be able to, say, for instance, you know, extract the code and maybe even use the title, you know, some sluggified title to then set a directory name, you know, and then we'd be trying to create, you know, files for, you know, the code snippets that we see, right?*

To implement a feature that watches for changes in a MongoDB collection and triggers specific procedures, you can use MongoDB's Change Streams. Change Streams allow you to listen for real-time changes in your MongoDB collections and act upon those changes as they occur. You can then register additional features for processing the conversations, such as extracting code snippets and creating files based on conversation titles.

Here's a step-by-step guide on how you might implement this:

1. **Set Up Change Streams**: Use MongoDB Change Streams to watch for changes in the desired collection.
2. **Process Changes**: Define the procedures to process new entries.
3. **Register Additional Features**: Allow registration of additional features to process the conversations, such as extracting code snippets and saving them to files.

### **Step 1: Set Up Change Streams**

First, make sure your MongoDB instance supports Change Streams (requires MongoDB 3.6 or later and a replica set).

### **Step 2: Define a Watcher Class**

Create a class to handle watching the collection and triggering procedures:

```python
import pymongo
from pymongo import MongoClient
from typing import List, Dict, Any, Callable
import time
import os

class MongoDBWatcher:
    def __init__(self, db_uri: str, db_name: str, collection_name: str, username: str, password: str):
        self.client = MongoClient(db_uri, username=username, password=password)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.handlers: List[Callable[[Dict[str, Any]], None]] = []

    def register_handler(self, handler: Callable[[Dict[str, Any]], None]):
        self.handlers.append(handler)

    def watch(self):
        with self.collection.watch() as stream:
            for change in stream:
                if change['operationType'] == 'insert':
                    document = change['fullDocument']
                    for handler in self.handlers:
                        handler(document)

    def extract_code_snippets(self, document: Dict[str, Any]):
        # Extract code snippets from the conversation document
        messages = document.get('message_set', [])
        snippets = []
        for message in messages:
            content = message.get('content', '')
            # Example of extracting code blocks, this could be improved
            code_blocks = self._extract_code_blocks(content)
            snippets.extend(code_blocks)
        return snippets

    def _extract_code_blocks(self, text: str) -> List[str]:
        # Dummy implementation, should be replaced with actual code extraction logic
        # Assuming code blocks are surrounded by triple backticks for simplicity
        code_blocks = []
        if "```" in text:
            parts = text.split("```")
            for i in range(1, len(parts), 2):
                code_blocks.append(parts[i])
        return code_blocks

    def save_snippets_to_files(self, document: Dict[str, Any]):
        title = document.get('title', 'untitled')
        sluggified_title = title.lower().replace(' ', '_')
        directory = os.path.join('conversations', sluggified_title)
        os.makedirs(directory, exist_ok=True)

        snippets = self.extract_code_snippets(document)
        for i, snippet in enumerate(snippets):
            file_path = os.path.join(directory, f'snippet_{i + 1}.txt')
            with open(file_path, 'w') as file:
                file.write(snippet)

        print(f"Saved {len(snippets)} snippets to {directory}")

# Example usage:
if __name__ == "__main__":
    watcher = MongoDBWatcher(
        db_uri="mongodb://localhost:27017",
        db_name="chatgpt_db",
        collection_name="conversations",
        username="root",
        password="example"
    )

    # Register the save_snippets_to_files handler
    watcher.register_handler(watcher.save_snippets_to_files)

    # Start watching the collection
    print("Starting to watch for changes...")
    watcher.watch()

```

### **Step 3: Register Additional Features**

You can extend this approach by registering additional features. For example, you could create more handlers for different types of processing and register them using the **`register_handler`** method.

### **Testing the Watcher**

To test this, you can insert a new document into the MongoDB collection from a MongoDB shell or another script, and the watcher should pick up the change and execute the registered handlers.

### **Notes**

1. **Change Stream Requirements**: Ensure your MongoDB instance is set up as a replica set, even if it's a single node, to use Change Streams.
2. **Error Handling**: Add appropriate error handling to the watcher to handle disconnections and other potential issues.
3. **Performance Considerations**: For a production environment, consider the performance implications and potential need for scaling, especially if processing involves heavy operations.

This approach gives you a flexible way to handle real-time updates and extend your processing capabilities as needed.

How should I be recording into maybe a new Mongo collection some of these processed results for further refinement?

To record processed results into a new MongoDB collection, you can modify your **`MongoDBWatcher`** class to include methods for saving these results. This approach allows you to store the processed data for further refinement and analysis.

Here's an example of how you can extend your class to save processed results:

### **Step 1: Extend MongoDBWatcher Class**

Add a method to save processed results into a new collection. You can name this collection **`processed_results`** or something similar.

```python
import pymongo
from pymongo import MongoClient
from typing import List, Dict, Any, Callable
import time
import os

class MongoDBWatcher:
    def __init__(self, db_uri: str, db_name: str, collection_name: str, username: str, password: str):
        self.client = MongoClient(db_uri, username=username, password=password)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.processed_collection = self.db['processed_results']
        self.handlers: List[Callable[[Dict[str, Any]], None]] = []

    def register_handler(self, handler: Callable[[Dict[str, Any]], None]):
        self.handlers.append(handler)

    def watch(self):
        with self.collection.watch() as stream:
            for change in stream:
                if change['operationType'] == 'insert':
                    document = change['fullDocument']
                    for handler in self.handlers:
                        handler(document)

    def extract_code_snippets(self, document: Dict[str, Any]):
        # Extract code snippets from the conversation document
        messages = document.get('message_set', [])
        snippets = []
        for message in messages:
            content = message.get('content', '')
            # Example of extracting code blocks, this could be improved
            code_blocks = self._extract_code_blocks(content)
            snippets.extend(code_blocks)
        return snippets

    def _extract_code_blocks(self, text: str) -> List[str]:
        # Dummy implementation, should be replaced with actual code extraction logic
        # Assuming code blocks are surrounded by triple backticks for simplicity
        code_blocks = []
        if "```" in text:
            parts = text.split("```")
            for i in range(1, len(parts), 2):
                code_blocks.append(parts[i])
        return code_blocks

    def save_snippets_to_files(self, document: Dict[str, Any]):
        title = document.get('title', 'untitled')
        sluggified_title = title.lower().replace(' ', '_')
        directory = os.path.join('conversations', sluggified_title)
        os.makedirs(directory, exist_ok=True)

        snippets = self.extract_code_snippets(document)
        for i, snippet in enumerate(snippets):
            file_path = os.path.join(directory, f'snippet_{i + 1}.txt')
            with open(file_path, 'w') as file:
                file.write(snippet)

        print(f"Saved {len(snippets)} snippets to {directory}")

        # Save the processed result to MongoDB
        processed_result = {
            'conversation_id': document['id'],
            'title': title,
            'snippets': snippets,
            'directory': directory,
            'processed_time': time.time()
        }
        self.save_processed_result(processed_result)

    def save_processed_result(self, result: Dict[str, Any]):
        self.processed_collection.insert_one(result)
        print(f"Processed result saved for conversation {result['conversation_id']}")

# Example usage:
if __name__ == "__main__":
    watcher = MongoDBWatcher(
        db_uri="mongodb://localhost:27017",
        db_name="chatgpt_db",
        collection_name="conversations",
        username="root",
        password="example"
    )

    # Register the save_snippets_to_files handler
    watcher.register_handler(watcher.save_snippets_to_files)

    # Start watching the collection
    print("Starting to watch for changes...")
    watcher.watch()

```

### **Step 2: Define the Processed Result Structure**

The **`save_processed_result`** method records the processed results into the **`processed_results`** collection. The structure of the processed result includes:

- **`conversation_id`**: The ID of the original conversation.
- **`title`**: The title of the conversation.
- **`snippets`**: The list of extracted code snippets.
- **`directory`**: The directory where the snippets are saved.
- **`processed_time`**: The timestamp when the processing was done.

### **Step 3: Query and Refine Processed Results**

You can now query the **`processed_results`** collection to refine and analyze the processed data further. For example:

```python
def query_processed_results(db, conversation_id=None):
    collection = db['processed_results']
    if conversation_id:
        results = collection.find({'conversation_id': conversation_id})
    else:
        results = collection.find()
    return list(results)

# Example usage:
if __name__ == "__main__":
    client = MongoClient("mongodb://localhost:27017", username="root", password="example")
    db = client['chatgpt_db']

    # Query all processed results
    processed_results = query_processed_results(db)
    for result in processed_results:
        print(result)

    # Query processed results for a specific conversation
    conversation_id = 'conv1'
    specific_results = query_processed_results(db, conversation_id)
    for result in specific_results:
        print(result)

```

### **Summary**

By recording processed results into a new MongoDB collection, you can easily track and refine the data over time. This setup allows for efficient data processing and retrieval, supporting further analysis and enhancements to your processing pipeline.

Would it make sense to have a collection that would be of files, and then each file could have properties of maybe what project or conversation that it were related to? Would that be easier?

Yes, creating a collection specifically for files with metadata about their related projects or conversations can be a very effective approach. This structure allows you to efficiently manage, query, and analyze files and their associations. Here's how you can implement it:

### **Step 1: Define the Schema for the Files Collection**

You can define a schema for the files collection where each document represents a file and contains metadata such as the project, conversation, file path, and other relevant properties.

### **Step 2: Update MongoDBWatcher to Save Files Metadata**

Modify the **`MongoDBWatcher`** class to save the metadata of the files into a new collection named **`files`**.

### **Step 3: Query and Manage Files**

You can then easily query this collection to find files related to specific projects or conversations.

Here's an example of how you can implement this:

```python
import pymongo
from pymongo import MongoClient
from typing import List, Dict, Any, Callable
import time
import os

class MongoDBWatcher:
    def __init__(self, db_uri: str, db_name: str, collection_name: str, username: str, password: str):
        self.client = MongoClient(db_uri, username=username, password=password)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.files_collection = self.db['files']
        self.handlers: List[Callable[[Dict[str, Any]], None]] = []

    def register_handler(self, handler: Callable[[Dict[str, Any]], None]):
        self.handlers.append(handler)

    def watch(self):
        with self.collection.watch() as stream:
            for change in stream:
                if change['operationType'] == 'insert':
                    document = change['fullDocument']
                    for handler in self.handlers:
                        handler(document)

    def extract_code_snippets(self, document: Dict[str, Any]):
        # Extract code snippets from the conversation document
        messages = document.get('message_set', [])
        snippets = []
        for message in messages:
            content = message.get('content', '')
            # Example of extracting code blocks, this could be improved
            code_blocks = self._extract_code_blocks(content)
            snippets.extend(code_blocks)
        return snippets

    def _extract_code_blocks(self, text: str) -> List[str]:
        # Dummy implementation, should be replaced with actual code extraction logic
        # Assuming code blocks are surrounded by triple backticks for simplicity
        code_blocks = []
        if "```" in text:
            parts = text.split("```")
            for i in range(1, len(parts), 2):
                code_blocks.append(parts[i])
        return code_blocks

    def save_snippets_to_files(self, document: Dict[str, Any]):
        title = document.get('title', 'untitled')
        sluggified_title = title.lower().replace(' ', '_')
        directory = os.path.join('conversations', sluggified_title)
        os.makedirs(directory, exist_ok=True)

        snippets = self.extract_code_snippets(document)
        for i, snippet in enumerate(snippets):
            file_path = os.path.join(directory, f'snippet_{i + 1}.txt')
            with open(file_path, 'w') as file:
                file.write(snippet)

            # Save the file metadata to MongoDB
            file_metadata = {
                'conversation_id': document['id'],
                'title': title,
                'file_path': file_path,
                'snippet': snippet,
                'processed_time': time.time()
            }
            self.save_file_metadata(file_metadata)

        print(f"Saved {len(snippets)} snippets to {directory}")

    def save_file_metadata(self, metadata: Dict[str, Any]):
        self.files_collection.insert_one(metadata)
        print(f"File metadata saved for conversation {metadata['conversation_id']}")

# Example usage:
if __name__ == "__main__":
    watcher = MongoDBWatcher(
        db_uri="mongodb://localhost:27017",
        db_name="chatgpt_db",
        collection_name="conversations",
        username="root",
        password="example"
    )

    # Register the save_snippets_to_files handler
    watcher.register_handler(watcher.save_snippets_to_files)

    # Start watching the collection
    print("Starting to watch for changes...")
    watcher.watch()

```

### **Querying the Files Collection**

You can then query the **`files`** collection to find files related to specific projects or conversations. Here's how you can do it:

```python
def query_files(db, conversation_id=None, project=None):
    collection = db['files']
    query = {}
    if conversation_id:
        query['conversation_id'] = conversation_id
    if project:
        query['project'] = project
    return list(collection.find(query))

# Example usage:
if __name__ == "__main__":
    client = MongoClient("mongodb://localhost:27017", username="root", password="example")
    db = client['chatgpt_db']

    # Query all files
    all_files = query_files(db)
    for file in all_files:
        print(file)

    # Query files for a specific conversation
    conversation_id = 'conv1'
    conversation_files = query_files(db, conversation_id=conversation_id)
    for file in conversation_files:
        print(file)

```
