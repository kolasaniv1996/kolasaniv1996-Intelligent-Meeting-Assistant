# Inter-Agent Communication Protocol (Conceptual)

This document defines a basic message format for communication between AI agents within the Gen AI Work Buddy system. The goal is to have a standardized way for agents to exchange information, requests, and notifications.

## Message Format

All inter-agent messages will be JSON objects with a common envelope structure.

```json
{
  "message_id": "unique_message_identifier_string", // UUID recommended
  "sender_agent_id": "agent_id_of_the_sender",
  "recipient_agent_id": "agent_id_of_the_recipient", // Can be a specific agent or a topic/group
  "timestamp": "iso_8601_datetime_utc",
  "message_type": "enum_string", // Defines the purpose/type of the message
  "version": "protocol_version_string", // e.g., "1.0"
  "payload": {
    // Message-type-specific data structure
  },
  "metadata": { // Optional: for routing hints, priority, etc.
    "priority": "NORMAL", // "HIGH", "LOW"
    "requires_ack": false, // boolean: Does the sender expect an acknowledgement?
    "trace_id": "optional_trace_id_for_distributed_tracing"
  }
}
```

## Key Envelope Fields:

*   `message_id`: A unique ID for tracking and debugging.
*   `sender_agent_id`: Identifies the originator of the message.
*   `recipient_agent_id`: Identifies the target. This could be a specific agent's ID or a broadcast/multicast address (e.g., a topic name like `project_X_agents`).
*   `timestamp`: When the message was created by the sender.
*   `message_type`: A string indicating the nature of the message. This determines the schema of the `payload`. Examples below.
*   `version`: Version of this communication protocol.
*   `payload`: An object containing the actual data specific to the `message_type`.
*   `metadata`: Additional information about the message.

## Example Message Types & Payloads:

This is not an exhaustive list, but provides examples.

1.  **`USER_AVAILABILITY_UPDATE`**:
    *   Purpose: Inform other agents about the user's availability.
    *   `payload`:
        ```json
        {
          "user_id": "user_identifier",
          "status": "BUSY" // "AVAILABLE", "IN_MEETING", "FOCUS_MODE"
          "until": "iso_8601_datetime_utc" // Optional: when the status is expected to change
        }
        ```

2.  **`TASK_ASSIGNMENT_REQUEST`**:
    *   Purpose: Request another agent (or one in a group) to take on a task.
    *   `payload`:
        ```json
        {
          "task_id": "unique_task_id",
          "description": "Detailed description of the task",
          "source_meeting_id": "optional_meeting_id_where_task_originated",
          "requested_due_date": "iso_8601_datetime",
          "priority": "HIGH", // "MEDIUM", "LOW"
          "required_capabilities": ["JIRA_WRITER"]
        }
        ```

3.  **`PROJECT_UPDATE_NOTIFICATION`**:
    *   Purpose: Notify relevant agents about an update in a project.
    *   `payload`:
        ```json
        {
          "project_id": "jira_project_id",
          "tool_type": "JIRA", // "CONFLUENCE"
          "update_type": "NEW_ISSUE_CREATED", // "ISSUE_STATUS_CHANGED", "NEW_COMMENT"
          "item_id": "jira_issue_key_or_confluence_page_id",
          "summary": "Brief summary of the update"
        }
        ```

4.  **`MEETING_CONTEXT_SHARE`**:
    *   Purpose: Share context about an upcoming or ongoing meeting.
    *   `payload`:
        ```json
        {
            "meeting_id": "calendar_event_id",
            "topic": "Sprint Planning Q3",
            "attendees": ["user_id1", "user_id2"],
            "key_documents_links": ["confluence_link1"],
            "current_status_summary": "Waiting for updates from engineering."
        }
        ```

## Further Considerations:

*   **Schema Management**: How to manage and version payload schemas for different `message_type`s.
*   **Error Handling**: Standard error message formats if a message cannot be processed.
*   **Security**: Message signing or encryption if communication channels are not secure.
*   **Service Discovery**: How agents find the `communication_endpoints` of other agents (using the Agent Directory).

This protocol provides a basic framework. Specific `message_type`s and their `payload` schemas will be defined as needed for different interactions.
