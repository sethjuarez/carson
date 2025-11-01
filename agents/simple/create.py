import time
import click
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    ImageBasedHostedAgentDefinition,
    ProtocolVersionRecord,
    AgentContainerStatus,
    AgentProtocol,
)

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
@click.option(
    "--image",
    prompt="Container Image",
    help="The container image to use for the agent.",
)
@click.option(
    "--description",
    prompt="Agent Description",
    help="A description for the agent version being created.",
)
@click.option(
    "--env",
    multiple=True,
    help="Environment variables for the container in the format KEY=VALUE. Can be specified multiple times.",
)
def create_agent(
    project_endpoint: str,
    agent_name: str,
    environment_variables: dict[str, str],
    image: str,
    description: str,
):

    client = AIProjectClient(
        endpoint=project_endpoint, credential=DefaultAzureCredential()
    )
    with client:
        # Create a new version of a Hosted Agent
        agent = client.agents.create_version(
            agent_name=agent_name,
            definition=ImageBasedHostedAgentDefinition(
                container_protocol_versions=[
                    ProtocolVersionRecord(
                        protocol=AgentProtocol.RESPONSES, version="v1"
                    )
                ],
                cpu="1",
                memory="2Gi",
                image=image,
                # Add any environment variables your container needs here
                environment_variables=environment_variables,
            ),
            description=description,
        )
        print(
            f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})"
        )

        operation = client.agents.start_container(
            agent_name=agent.name,
            agent_version=agent.version,
            min_replicas=1,
            max_replicas=1,
        )
        print(
            f"Starting its container (operation id: {operation.id}, status: {operation.status})"
        )

        # Poll until the operation is done
        while operation.status in [
            AgentContainerStatus.NOT_STARTED,
            AgentContainerStatus.IN_PROGRESS,
        ]:
            time.sleep(5)
            operation = client.agents.retrieve_container_operation(
                agent_name=agent_name, operation_id=operation.id
            )
            print(f"    Operation status: {operation.status}")

        if operation.status == AgentContainerStatus.SUCCEEDED:
            container = client.agents.retrieve_container(
                agent_name=agent_name, agent_version=agent.version
            )
            print(
                f"Container status: {container.status}, created at: {container.created_at}"
            )
        elif operation.status == AgentContainerStatus.FAILED:
            print(f"Operation failed. Error message: {operation.error}")
        else:
            print(f"Unexpected operation status: {operation.status}")


if __name__ == "__main__":
    create_agent()