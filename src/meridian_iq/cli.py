"""Interactive CLI for presenting both Meridian IQ patterns."""

from __future__ import annotations

import json
from typing import Annotated

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from meridian_iq.config import Settings
from meridian_iq.patterns import run_multi_agent, run_prompt_agent
from meridian_iq.patterns.prompt_agent import DEFAULT_QUESTION

app = typer.Typer(
    help="Meridian Tax Advisors: Microsoft four-IQ knowledge demo",
    no_args_is_help=True,
)
console = Console()


def _render(result, json_output: bool = False) -> None:
    if json_output:
        console.print_json(
            json.dumps(
                {
                    "question": result.question,
                    "answer": result.answer,
                    "facts": [fact.as_dict() for fact in result.facts],
                    "trace": [
                        {
                            "actor": item.actor,
                            "action": item.action,
                            "sources": item.sources,
                        }
                        for item in result.trace
                    ],
                }
            )
        )
        return

    console.print(
        Panel.fit(
            f"[bold]Client:[/] Alex Rivera\n[bold]Question:[/] {result.question}",
            title="Meridian Tax Advisors",
            border_style="blue",
        )
    )
    trace = Table(title="Live orchestration trace", header_style="bold cyan")
    trace.add_column("Actor")
    trace.add_column("Action")
    trace.add_column("IQ / delegate")
    for item in result.trace:
        trace.add_row(item.actor, item.action, ", ".join(item.sources))
    console.print(trace)

    if result.facts:
        facts = Table(title="Grounding ledger", header_style="bold green")
        facts.add_column("IQ", no_wrap=True)
        facts.add_column("Fact")
        facts.add_column("Citation")
        for item in result.facts:
            facts.add_row(item.iq, item.fact, item.citation)
        console.print(facts)
    console.print(Markdown(result.answer))


@app.command("prompt")
def prompt_demo(
    question: Annotated[str, typer.Option("-q", "--question")] = DEFAULT_QUESTION,
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Run the single prompt-agent pattern."""
    load_dotenv()
    _render(run_prompt_agent(question, Settings.from_env()), json_output)


@app.command("multi")
def multi_agent_demo(
    question: Annotated[str, typer.Option("-q", "--question")] = DEFAULT_QUESTION,
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Run the Microsoft Agent Framework multi-agent pattern."""
    load_dotenv()
    _render(run_multi_agent(question, Settings.from_env()), json_output)


@app.command("all")
def all_patterns(
    question: Annotated[str, typer.Option("-q", "--question")] = DEFAULT_QUESTION,
) -> None:
    """Run both patterns side by side."""
    load_dotenv()
    settings = Settings.from_env()
    console.rule("[bold blue]Pattern 1: Foundry prompt agent")
    _render(run_prompt_agent(question, settings))
    console.rule("[bold magenta]Pattern 2: Agent Framework multi-agent")
    _render(run_multi_agent(question, settings))


if __name__ == "__main__":
    app()
