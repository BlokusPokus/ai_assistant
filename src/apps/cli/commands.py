import click

from personal_assistant.config.settings import settings
from personal_assistant.core.agent import AgentCore


@click.group()
def cli():
    """Personal Assistant CLI"""
    pass


@cli.command()
def status():
    """Check system status"""
    click.echo("Personal Assistant Status:")
    click.echo(f"Environment: {settings.ENVIRONMENT}")
    click.echo(f"Debug: {settings.DEBUG}")
    click.echo(f"Log Level: {settings.LOG_LEVEL}")


@cli.command()
@click.argument('message')
def process(message):
    """Process a message through the assistant"""
    agent = AgentCore()
    response = agent.process_message(message)
    click.echo(f"Response: {response}")


if __name__ == "__main__":
    cli()
