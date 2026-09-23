from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    FileSearchTool,
    StructuredInputDefinition,
)

endpoint = "https://eduvision-ai-resource.services.ai.azure.com/api/projects/eduvision-ai"

project = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential()
)

tool = FileSearchTool(
    vector_store_ids=["{{vector_store_id}}"]
)

agent = project.agents.create_version(
    agent_name="StudyMentor",
    definition=PromptAgentDefinition(
        model="gpt-5-mini",

        instructions="""
You are StudyMentor, an AI-powered personalized study assistant.

Use File Search whenever answering questions related to the student's
uploaded study material.

Base answers primarily on the retrieved study material.

If the requested information is not found, clearly say:

"I couldn't find this information in your uploaded study material."

Explain concepts simply, clearly, and in an exam-oriented way.

When the student asks for MCQs, generate questions only from
the uploaded study material.
""",

        tools=[tool],

        structured_inputs={
            "vector_store_id": StructuredInputDefinition(
                description="Vector store containing the student's uploaded notes",
                required=True,
                schema={"type": "string"},
            )
        },
    ),
)

print("StudyMentor File Search agent created!")
print("Version:", agent.version)