# Agent Directory Schema (Conceptual)

This document outlines a conceptual schema for an Agent Directory. This directory would store information about each registered AI agent, enabling discovery and understanding of their roles and associations.

## Agent Record Schema

Each agent record could have the following structure (represented in JSON):

```json
{
  "agent_id": "unique_agent_identifier_string", // e.g., "agent_user123_primary"
  "user_id": "associated_user_identifier_string", // Links to the human user
  "agent_type": "enum_string", // e.g., "PRIMARY_PERSONAL", "PROJECT_AGENT", "MEETING_COORDINATOR"
  "status": "enum_string", // e.g., "ACTIVE", "INACTIVE", "DISABLED"
  "display_name": "Human-readable agent name", // e.g., "User One's Work Buddy"
  "capabilities": [ // List of capabilities or specializations
    "CALENDAR_MANAGEMENT",
    "JIRA_READER",
    "CONFLUENCE_READER"
    // "JIRA_WRITER", "MEETING_PARTICIPANT_AUDIO", etc.
  ],
  "associated_projects": [ // For PROJECT_AGENT type
    {
      "project_id": "jira_project_id_or_key",
      "tool_type": "JIRA",
      "role": "READER" // or "WRITER", "ADMIN"
    }
  ],
  "associated_spaces": [ // For PROJECT_AGENT type (or if agents manage Confluence spaces)
    {
      "space_id": "confluence_space_key",
      "tool_type": "CONFLUENCE",
      "role": "READER" // or "WRITER"
    }
  ],
  "communication_endpoints": { // How to reach this agent
    "message_queue_topic": "agent_specific_topic_name", // e.g., "agents.agent_user123_primary.messages"
    // "http_callback_url": "https://example.com/agent/callback" // (Alternative)
  },
  "preferences_reference_id": "reference_to_user_personalization_settings",
  "last_active_timestamp": "iso_8601_datetime",
  "created_timestamp": "iso_8601_datetime",
  "updated_timestamp": "iso_8601_datetime",
  "metadata": { // For any other custom data
    "version": "1.0",
    "custom_tags": ["engineering_team_agent"]
  }
}
```

## Key Fields Explanation:

*   `agent_id`: Primary key for the agent.
*   `user_id`: Foreign key linking to the user this agent serves.
*   `agent_type`: Defines the agent's role (Primary, Project-specific, temporary Meeting Coordinator).
*   `status`: Current operational status of the agent.
*   `capabilities`: Defines what the agent can do (e.g., read calendar, write to Jira). This is crucial for smart routing.
*   `associated_projects`/`associated_spaces`: Links project agents to specific Jira projects or Confluence spaces.
*   `communication_endpoints`: Specifies how other agents or services can send messages to this agent (e.g., its dedicated message queue topic).
*   `preferences_reference_id`: Link to where detailed personalization settings are stored.

## Future Considerations:

*   **Scalability**: For a large number of agents, efficient querying and indexing will be vital.
*   **Security**: Access control for who can view/modify agent records.
*   **Dynamic Registration/Deregistration**: How new agents are added or removed.
*   **Health Checks**: Mechanism to monitor agent health.

This schema will likely evolve as the system is developed. It provides a starting point for what data needs to be managed for each agent.
