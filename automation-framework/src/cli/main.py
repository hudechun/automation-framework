"""
CLI主入口
"""
import click
import asyncio
from pathlib import Path
from ..sdk import AutomationClient


@click.group()
@click.option("--base-url", default="http://localhost:8000", help="API base URL")
@click.option("--api-key", envvar="AUTOMATION_API_KEY", help="API key")
@click.pass_context
def cli(ctx, base_url, api_key):
    """Automation Framework CLI"""
    ctx.ensure_object(dict)
    ctx.obj["base_url"] = base_url
    ctx.obj["api_key"] = api_key


@cli.group()
def task():
    """Task management commands"""
    pass


@task.command("list")
@click.option("--limit", default=10, help="Number of tasks to show")
@click.pass_context
def task_list(ctx, limit):
    """List tasks"""
    async def _list():
        async with AutomationClient(ctx.obj["base_url"], ctx.obj["api_key"]) as client:
            tasks = await client.tasks.list(limit=limit)
            for t in tasks:
                click.echo(f"{t['id']}: {t['name']} - {t['status']}")
    
    asyncio.run(_list())


@task.command("create")
@click.argument("name")
@click.option("--description", default="", help="Task description")
@click.pass_context
def task_create(ctx, name, description):
    """Create a new task"""
    async def _create():
        async with AutomationClient(ctx.obj["base_url"], ctx.obj["api_key"]) as client:
            task = await client.tasks.create(name=name, description=description, actions=[])
            click.echo(f"Created task: {task['id']}")
    
    asyncio.run(_create())


@task.command("execute")
@click.argument("task_id")
@click.option("--wait", is_flag=True, help="Wait for completion")
@click.pass_context
def task_execute(ctx, task_id, wait):
    """Execute a task"""
    async def _execute():
        async with AutomationClient(ctx.obj["base_url"], ctx.obj["api_key"]) as client:
            if wait:
                result = await client.tasks.execute_and_wait(task_id)
                click.echo(f"Task completed: {result['status']}")
            else:
                await client.tasks.execute(task_id)
                click.echo(f"Task started: {task_id}")
    
    asyncio.run(_execute())


@cli.group()
def config():
    """Configuration management commands"""
    pass


@config.command("init")
@click.option("--config-dir", default=".automation", help="Config directory")
def config_init(config_dir):
    """Initialize configuration"""
    config_path = Path(config_dir)
    config_path.mkdir(parents=True, exist_ok=True)
    
    config_file = config_path / "config.json"
    if not config_file.exists():
        import json
        default_config = {
            "base_url": "http://localhost:8000",
            "api_key": ""
        }
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=2)
        click.echo(f"Created config file: {config_file}")
    else:
        click.echo("Config file already exists")


if __name__ == "__main__":
    cli()
