# Issue Model

## Background

The Scaled Agile Framework (SAFe) extends Agile principles to large organizations. It provides a structured approach to scaling Agile across multiple teams, departments, and even entire enterprises. SAFe incorporates practices from Agile, Lean, and DevOps to deliver complex solutions efficiently. It emphasizes alignment, collaboration, and delivery across large numbers of Agile teams through a framework that includes various levels such as Team, Program, Large Solution, and Portfolio.

When doing Agile Software Development for a military defense contractor, several particular considerations include:

Security and Compliance: Ensure all development processes comply with stringent security standards and regulations. This includes data protection, secure coding practices, and regular security audits.

Documentation: Maintain thorough and precise documentation due to the regulatory requirements and the critical nature of defense projects. This might contrast with the Agile principle of valuing working software over comprehensive documentation.

Risk Management: Implement robust risk management practices to address the potential high stakes involved in defense projects. Regular risk assessments and mitigation plans are crucial.

Stakeholder Engagement: Engage with various stakeholders, including government agencies, military personnel, and other contractors, ensuring their requirements are met and they are kept informed throughout the project.

Iterative Testing: Continuous integration and testing are vital to ensure that the software meets the high reliability and performance standards expected in military applications. This includes rigorous unit testing, system testing, and field testing.

Change Management: Be prepared for changes in requirements due to evolving defense needs or new regulatory guidelines. Agile's flexibility is beneficial here, but changes must be managed carefully to maintain compliance and project scope.

Clear Communication: Foster clear and frequent communication within and across teams to ensure alignment and understanding of project goals, especially given the complexity and scale of defense projects.

## Jira Issue Types for Defense Projects

In JIRA, issues are various types of work items that represent tasks to be completed. Here's how capabilities, epochs, stories, and tasks fit into the JIRA framework:

* Capabilities represent broad, high-level functions.
* Epics break down capabilities into more manageable parts.
* Stories provide detailed, user-focused requirements.
* Tasks are specific actions to be completed to fulfill stories or epics.


### Capability

A capability is a high-level function or feature that an organization aims to deliver. It is typically broader in scope than an individual project and often requires the coordinated effort of multiple teams. In JIRA, capabilities are not always standard issue types, but they can be created as custom issue types if needed, often managed at the portfolio or program level.

### Epic

An epic is a large body of work that can be broken down into smaller tasks or stories. It represents a significant deliverable or milestone that encompasses many smaller, related tasks. In JIRA, epics help organize and track large projects by grouping related stories and tasks.

### Story

A story, also known as a user story, is a short, simple description of a feature or functionality from the perspective of the end-user. Stories are typically small enough to be completed within a single sprint. In JIRA, stories are used to capture specific requirements and are often part of an epic.

### Task

A task is a specific piece of work that needs to be completed, often technical or operational in nature. Tasks are typically smaller than stories and represent individual work items that team members need to accomplish. In JIRA, tasks can be stand-alone items or can be linked to stories or epics.



## Product Development

In the context of product development, the hierarchy of JIRA issues helps break down the work required to develop and deliver product features. Here's how capabilities, epics, stories, and tasks relate to product features:

**Capability**: A capability is often a large-scale business requirement or a strategic function that the product must support. It is broader than a single feature and might encompass several related features. For instance, "Enhanced User Security" could be a capability encompassing features like two-factor authentication, biometric login, and encryption.

**Epic**: An epic is a substantial piece of work that can deliver a specific product feature or a set of related features. It breaks down the capability into more manageable parts that can be delivered incrementally. For example, if the capability is "Enhanced User Security," an epic might be "Implement Two-Factor Authentication."

**Story**: A story is a user-centric description of a feature or a part of a feature. It focuses on delivering specific value to the end-user and is typically small enough to be completed within a single sprint. Stories break down epics into detailed, actionable requirements. For instance, under the epic "Implement Two-Factor Authentication," you might have stories like "As a user, I want to receive a code via SMS to authenticate my login."

**Task**: A task represents a specific piece of work needed to complete a story. Tasks are more granular and often technical. For example, under the story "As a user, I want to receive a code via SMS to authenticate my login," tasks might include "Set up SMS gateway," "Create user interface for code entry," and "Implement backend logic for code validation."

So, in product development:

* Capabilities represent broad, strategic business objectives that the product needs to support.
* Epics are large features or significant deliverables that contribute to these capabilities.
* Stories are detailed descriptions of the functionality from the user's perspective, breaking down epics into manageable pieces.
* Tasks are the specific actions required to implement the stories.


## Software Development

### Datamodel

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class IssueType(str, Enum):
    CAPABILITY = "capability"
    EPIC = "epic"
    STORY = "story"
    TASK = "task"

class Issue(BaseModel):
    issue_id: str = Field(..., description="Unique identifier for the issue")
    title: str = Field(..., description="Title of the issue")
    description: Optional[str] = Field(None, description="Detailed description of the issue")
    issue_type: IssueType = Field(..., description="Type of the issue")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp of the issue")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp of the issue")
    reporter: str = Field(..., description="User who reported the issue")
    assignee: Optional[str] = Field(None, description="User assigned to the issue")
    status: str = Field(..., description="Current status of the issue")
    labels: List[str] = Field(default_factory=list, description="Labels associated with the issue")

    class Config:
        use_enum_values = True
```

### Derived Classes

```python

class Capability(Issue):
    issue_type: IssueType = Field(default=IssueType.CAPABILITY, const=True)
    strategic_goal: Optional[str] = Field(None, description="Strategic goal associated with this capability")

class Epic(Issue):
    issue_type: IssueType = Field(default=IssueType.EPIC, const=True)
    capabilities: List[str] = Field(default_factory=list, description="List of capabilities this epic is related to")
    stories: List[str] = Field(default_factory=list, description="List of stories under this epic")

class Story(Issue):
    issue_type: IssueType = Field(default=IssueType.STORY, const=True)
    epic_id: Optional[str] = Field(None, description="The ID of the epic this story belongs to")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Acceptance criteria for the story")
    tasks: List[str] = Field(default_factory=list, description="List of tasks for this story")

class Task(Issue):
    issue_type: IssueType = Field(default=IssueType.TASK, const=True)
    story_id: Optional[str] = Field(None, description="The ID of the story this task belongs to")
    due_date: Optional[datetime] = Field(None, description="Due date for the task")

```


### Alternative Approach with Relations

Define the base Issue and Relation classes.
Derive specific relationship classes for different types of relationships (e.g., CapabilityToEpicRelation, EpicToStoryRelation).

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum
from datetime import datetime

class IssueType(str, Enum):
    CAPABILITY = "capability"
    EPIC = "epic"
    STORY = "story"
    TASK = "task"

class Issue(BaseModel):
    issue_id: str = Field(..., description="Unique identifier for the issue")
    title: str = Field(..., description="Title of the issue")
    description: Optional[str] = Field(None, description="Detailed description of the issue")
    issue_type: IssueType = Field(..., description="Type of the issue")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp of the issue")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp of the issue")
    reporter: str = Field(..., description="User who reported the issue")
    assignee: Optional[str] = Field(None, description="User assigned to the issue")
    status: str = Field(..., description="Current status of the issue")
    labels: List[str] = Field(default_factory=list, description="Labels associated with the issue")

    class Config:
        use_enum_values = True

class Capability(Issue):
    issue_type: IssueType = Field(default=IssueType.CAPABILITY, const=True)
    strategic_goal: Optional[str] = Field(None, description="Strategic goal associated with this capability")

class Epic(Issue):
    issue_type: IssueType = Field(default=IssueType.EPIC, const=True)
    capabilities: List[str] = Field(default_factory=list, description="List of capabilities this epic is related to")
    stories: List[str] = Field(default_factory=list, description="List of stories under this epic")

class Story(Issue):
    issue_type: IssueType = Field(default=IssueType.STORY, const=True)
    epic_id: Optional[str] = Field(None, description="The ID of the epic this story belongs to")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Acceptance criteria for the story")
    tasks: List[str] = Field(default_factory=list, description="List of tasks for this story")

class Task(Issue):
    issue_type: IssueType = Field(default=IssueType.TASK, const=True)
    story_id: Optional[str] = Field(None, description="The ID of the story this task belongs to")
    due_date: Optional[datetime] = Field(None, description="Due date for the task")

class Relation(BaseModel):
    source_id: str = Field(..., description="The ID of the source issue")
    destination_id: str = Field(..., description="The ID of the destination issue")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp of the relation")
    relation_type: str = Field(..., description="Type of the relationship")

    @validator('relation_type')
    def validate_relation_type(cls, value):
        valid_relation_types = {"capability_to_epic", "epic_to_story", "story_to_task"}
        if value not in valid_relation_types:
            raise ValueError("Invalid relation type")
        return value

class CapabilityToEpicRelation(Relation):
    relation_type: str = Field(default="capability_to_epic", const=True)

    @validator('source_id', 'destination_id')
    def validate_ids(cls, value, values, field):
        # Fetch the issues from the database using the IDs to check their types (pseudo-code)
        source_issue = get_issue_by_id(values['source_id'])  # Replace with actual database fetch logic
        destination_issue = get_issue_by_id(values['destination_id'])  # Replace with actual database fetch logic
        if source_issue.issue_type != IssueType.CAPABILITY or destination_issue.issue_type != IssueType.EPIC:
            raise ValueError("Invalid issue types for Capability to Epic relation")
        return value

class EpicToStoryRelation(Relation):
    relation_type: str = Field(default="epic_to_story", const=True)

    @validator('source_id', 'destination_id')
    def validate_ids(cls, value, values, field):
        source_issue = get_issue_by_id(values['source_id'])  # Replace with actual database fetch logic
        destination_issue = get_issue_by_id(values['destination_id'])  # Replace with actual database fetch logic
        if source_issue.issue_type != IssueType.EPIC or destination_issue.issue_type != IssueType.STORY:
            raise ValueError("Invalid issue types for Epic to Story relation")
        return value

class StoryToTaskRelation(Relation):
    relation_type: str = Field(default="story_to_task", const=True)

    @validator('source_id', 'destination_id')
    def validate_ids(cls, value, values, field):
        source_issue = get_issue_by_id(values['source_id'])  # Replace with actual database fetch logic
        destination_issue = get_issue_by_id(values['destination_id'])  # Replace with actual database fetch logic
        if source_issue.issue_type != IssueType.STORY or destination_issue.issue_type != IssueType.TASK:
            raise ValueError("Invalid issue types for Story to Task relation")
        return value

# Pseudo function to fetch issues by ID
def get_issue_by_id(issue_id: str) -> Issue:
    # Replace with actual database fetch logic
    pass
```

### **Atomic and Composite Relationships**

For more atomic relationships, you can define single-source-to-single-destination relationships and then compose these into more complex relationships:

```python

class AtomicRelation(BaseModel):
    source_id: str = Field(..., description="The ID of the source issue")
    destination_id: str = Field(..., description="The ID of the destination issue")
    relation_type: str = Field(..., description="Type of the relationship")

class CompositeRelation(BaseModel):
    atomic_relations: List[AtomicRelation] = Field(..., description="List of atomic relationships")

    @validator('atomic_relations')
    def validate_atomic_relations(cls, value):
        # Placeholder for actual validation logic
        # Ensure that all atomic relations are valid
        return value

```

### **Example Usage**

Here's how you might use these models:

```python
# Creating atomic relationships
atomic_relation1 = AtomicRelation(source_id="capability1", destination_id="epic1", relation_type="capability_to_epic")
atomic_relation2 = AtomicRelation(source_id="epic1", destination_id="story1", relation_type="epic_to_story")

# Creating a composite relationship
composite_relation = CompositeRelation(atomic_relations=[atomic_relation1, atomic_relation2])

# Many-to-one relationship
many_to_one_relation = ManyToOneRelation(source_ids=["story1", "story2"], destination_id="epic1")

# One-to-many relationship
one_to_many_relation = OneToManyRelation(source_id="epic1", destination_ids=["story1", "story2"])

# Many-to-many relationship
many_to_many_relation = ManyToManyRelation(source_ids=["epic1", "epic2"], destination_ids=["story1", "story2"])

```

This setup allows for flexible and complex relationship management between issues, ensuring that you can handle various cardinalities and maintain clear validation rules. Each relationship type can be validated to ensure that only appropriate issue types are related.
