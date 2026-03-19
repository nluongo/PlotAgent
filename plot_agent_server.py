"""
MCP server for the PlotAgent AI agent workflow.

Exposes three tools:
  - load_plot(image_path)           → returns an image content block for visual inspection
  - apply_plot_override(...)        → writes per-plot overrides to configs/plots.yaml
  - run_makePlot(args)              → runs makePlot.py and returns stdout+stderr

Design principle: pure I/O — no LLM calls inside this server.
The calling agent (Claude) does all reasoning and visual evaluation.
"""

import base64
import shlex
import subprocess
from pathlib import Path

import yaml
from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent

REPO_ROOT = Path(__file__).parent.resolve()
PLOTS_YAML = REPO_ROOT / "configs" / "plots.yaml"

mcp = FastMCP("plot-agent")


@mcp.tool()
def load_plot(image_path: str) -> list[ImageContent]:
    """Return a plot image so the calling agent can evaluate it visually.

    Args:
        image_path: Absolute or repo-relative path to a PNG or PDF file.
    """
    path = Path(image_path)
    if not path.is_absolute():
        path = REPO_ROOT / path

    if not path.exists():
        raise FileNotFoundError(f"Plot not found: {path}")

    mime = "image/png" if path.suffix.lower() == ".png" else "application/pdf"
    data = base64.standard_b64encode(path.read_bytes()).decode("ascii")
    return [ImageContent(type="image", data=data, mimeType=mime)]


@mcp.tool()
def apply_plot_override(histogram: str, selection: str, overrides: dict) -> str:
    """Add or update a per-plot override entry in configs/plots.yaml.

    Finds the entry whose `histogram` and `selection` fields match, or appends
    a new entry if none exists. Merges `overrides` into the matched entry.
    Idempotent: calling with the same arguments twice is safe.

    Args:
        histogram: Histogram key, e.g. "bbll_mll_NOSYS".
        selection: Selection key, e.g. "Signal_Region".
        overrides: Dict of override fields, e.g. {"x_max": 500, "log_scale": true}.

    Returns:
        Confirmation string describing what was written.
    """
    # Load existing YAML (may be empty or have no 'plots' key yet)
    raw = PLOTS_YAML.read_text() if PLOTS_YAML.exists() else ""
    doc = yaml.safe_load(raw) or {}

    plots: list[dict] = doc.get("plots", []) or []

    # Find existing entry
    matched = None
    for entry in plots:
        if entry.get("histogram") == histogram and entry.get("selection") == selection:
            matched = entry
            break

    if matched is not None:
        matched.update(overrides)
        action = "updated"
    else:
        new_entry = {"histogram": histogram, "selection": selection, **overrides}
        plots.append(new_entry)
        doc["plots"] = plots
        action = "appended"

    # Preserve the header comment by prepending it back
    header_lines = []
    for line in raw.splitlines():
        if line.startswith("#"):
            header_lines.append(line)
        else:
            break
    header = "\n".join(header_lines) + "\n" if header_lines else ""

    PLOTS_YAML.write_text(header + yaml.dump(doc, default_flow_style=False, sort_keys=False))

    return (
        f"{action} entry: histogram={histogram!r}, selection={selection!r}, "
        f"overrides={overrides}"
    )


@mcp.tool()
def run_makePlot(args: str = "-r -s") -> str:
    """Run makePlot.py with the given arguments. Returns combined stdout+stderr.

    Args:
        args: Command-line arguments string, e.g. "-r -s" or "-r -s -l".

    Returns:
        Combined stdout and stderr output plus the exit code.
    """
    cmd = ["python3", "makePlot.py"] + shlex.split(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    output = ""
    if result.stdout:
        output += result.stdout
    if result.stderr:
        output += result.stderr
    output += f"\n[exit code: {result.returncode}]"
    return output


if __name__ == "__main__":
    mcp.run()
