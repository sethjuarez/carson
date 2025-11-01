import click
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.core.exceptions import ResourceNotFoundError

load_dotenv()


@click.command()
@click.option(
    "--project-endpoint",
    prompt="Project Endpoint",
    help="The endpoint URL of the AI Project.",
)
@click.option(
    "--agent-name",
    prompt="Agent Name",
    help="The name of the agent to deploy.",
)
def exists(
    project_endpoint: str,
    agent_name: str,
):

    client = AIProjectClient(
        endpoint=project_endpoint, credential=DefaultAzureCredential()
    )
    with client:
        # Retrieve latest version of an Agent
        try:
            agent = client.agents.retrieve(agent_name=agent_name)
        except ResourceNotFoundError as _:
            print(f"Could not find Agent named {agent_name}")
            return {}

        print(f"Agent retrieved (id: {agent.id}, name: {agent.name})")

        # List all versions of an Agent and retrieve their container status
        versions = []
        for version in client.agents.list_versions(agent_name=agent_name):
            container = client.agents.retrieve_container(
                agent_name=agent_name, agent_version=version.version
            )
            versions.append(
                {
                    "version": version.version,
                    "description": version.description,
                    "created_at": version.created_at,
                    "container": container.as_dict(),
                }
            )
        return versions


if __name__ == "__main__":
    exists()
