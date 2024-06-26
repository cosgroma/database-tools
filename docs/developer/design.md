# Application Design

## Introduction

### **Project Overview**

This project involves creating an application to watch for changes in a MongoDB collection and process those changes by extracting code snippets, saving them as files, and recording the processed results into a separate MongoDB collection. The app should be able to handle new entries, register additional features for processing, and manage the metadata of files.

### **Critical Requirements**

1. **MongoDB Change Stream Integration**:
    - The app must use MongoDB Change Streams to watch for changes in a specified collection.
    - The app should handle **`insert`** operations and process the new documents accordingly.
2. **File Management**:
    - Extract code snippets from the conversation messages.
    - Save code snippets as files in a directory named based on a sluggified title of the conversation.
    - Store file metadata in a **`files`** collection in MongoDB, including conversation ID, title, file path, snippet content, and processed time.
3. **Metadata Storage**:
    - Save processed results and file metadata in separate collections for further analysis and refinement.
    - Ensure that the stored metadata includes all relevant properties for querying and managing the files.
4. **Feature Registration**:
    - Allow for registering additional processing features that can be triggered by new entries in the watched collection.
    - Ensure that these features can be easily extended and integrated into the processing pipeline.

### **Critical Functions**

1. **MongoDBWatcher Class**:
    - Initialize the MongoDB client and set up the required collections.
    - Register handlers for processing new entries.
    - Watch the specified collection for changes using Change Streams.
2. **Extract and Save Code Snippets**:
    - Extract code snippets from the content of conversation messages.
    - Save the extracted snippets as files in a structured directory.
    - Record metadata about the saved files in the **`files`** collection.
3. **Save Processed Results**:
    - Save metadata about the processed conversations in a separate collection for further refinement.
    - Ensure that all relevant properties are stored and can be queried efficiently.
4. **Query and Manage Files**:
    - Implement functions to query the **`files`** collection based on conversation ID, project, or other criteria.
    - Provide a structured way to manage and analyze the processed data.


## Architecture

### **System Components**

1. **MongoDB Database**:
    - **`conversations`** Collection: Contains the conversation data to be watched for changes.
    - **`files`** Collection: Stores metadata about the saved code snippets.
    - **`processed_results`** Collection: Records processed results and metadata for further analysis.
2. **MongoDBWatcher Class**:
    - **`MongoDBWatcher`**: Handles the integration with MongoDB Change Streams.
    - **`FileProcessor`**: Extracts and saves code snippets from conversation messages.
    - **`
