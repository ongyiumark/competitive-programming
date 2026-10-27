"""Shared data structures and Markdown generation utilities."""

from dataclasses import dataclass, field
import os
import re
from typing import Literal

CONTESTS_CACHE = "contest_data/contests.json"
ATCODER_PATH = "AtCoder"
CODEFORCES_PATH = "Codeforces"
ATCODER_DOMAIN = "https://atcoder.jp"
CODEFORCES_DOMAIN = "https://codeforces.com"

SOLUTION_EXTENSIONS = {".cpp", ".cc", ".c", ".py", ".java", ".rs", ".go"}


def natural_sort_key(s: str) -> list[int | str]:
  """Sort key that orders alphanumeric strings naturally (e.g. 'ABC9' before 'ABC10')."""
  return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def is_solution_file(filename: str) -> bool:
  """Returns True if the filename looks like a valid contest solution file."""
  if filename.startswith("."):
    return False
  base, ext = os.path.splitext(filename)
  if ext.lower() not in SOLUTION_EXTENSIONS:
    return False
  parts = base.split("_", 1)
  return len(parts) == 2 and bool(parts[0]) and bool(parts[1])


def parse_solution_filename(filename: str) -> tuple[str, str]:
  """Extracts (contest_code, task_code) from a filename like 'ABC450_A.py'."""
  base, _ = os.path.splitext(os.path.basename(filename))
  contest_code, rest = base.split("_", 1)
  task_code = rest.split("_", 1)[0]
  return contest_code.upper(), task_code.upper()


@dataclass
class Task:
  """Represents a single contest problem/task."""
  task_code: str
  task_name: str
  task_link: str

  def to_dict(self) -> dict[str, str]:
    """Serializes task metadata to a dictionary."""
    return {
      "name": self.task_name,
      "link": self.task_link,
    }


@dataclass
class Contest:
  """Represents a competitive programming contest and its tasks."""
  contest_code: str
  contest_name: str
  tasks: list[Task] = field(default_factory=list)

  def __len__(self) -> int:
    return len(self.tasks)

  def add_task(self, task: Task) -> None:
    """Appends a task to the contest."""
    self.tasks.append(task)

  def to_dict(self) -> dict:
    """Serializes the contest and its tasks for JSON caching."""
    return {
      "name": self.contest_name,
      "tasks": {task.task_code: task.to_dict() for task in self.tasks},
    }

  @classmethod
  def from_dict(cls, contest_code: str, data: dict) -> "Contest":
    """Deserializes a Contest instance from cached JSON dictionary data."""
    tasks = [
      Task(task_code=code, task_name=info["name"], task_link=info["link"])
      for code, info in data.get("tasks", {}).items()
    ]
    return cls(
      contest_code=contest_code,
      contest_name=data["name"],
      tasks=tasks,
    )


class Markdown:
  """Helper utilities for generating and updating Markdown sections."""

  @staticmethod
  def collapsed_section(summary: str, lines: list[str]) -> str:
    """Returns a collapsible <details> block in Markdown."""
    body = "\n".join(lines)
    return f"<details>\n<summary>{summary}</summary>\n\n{body}\n</details>"

  @staticmethod
  def link(text: str, href: str) -> str:
    """Returns a Markdown link."""
    return f"[{text}]({href})"

  @staticmethod
  def header(text: str, level: int = 1) -> str:
    """Returns a Markdown heading of the specified level."""
    return f"{'#' * level} {text}"

  @staticmethod
  def table(
    header: list[str],
    alignment: list[Literal["l", "r", "c"]],
    data: list[list[str]],
  ) -> str:
    """Generates a Markdown table from column-oriented data."""
    if len(header) != len(alignment):
      raise RuntimeError(
        f"Header has {len(header)} columns, but alignment has {len(alignment)}."
      )
    if len(header) != len(data):
      raise RuntimeError(
        f"Header has {len(header)} columns, but data has {len(data)}."
      )
    if len(header) == 0:
      raise RuntimeError("Number of columns must be 1 or greater.")

    num_rows = len(data[0])
    for col in data[1:]:
      if len(col) != num_rows:
        raise RuntimeError("Number of rows must be the same for all columns.")

    align_map = {"l": ":-", "r": "-:", "c": ":-:"}
    for a in alignment:
      if a not in align_map:
        raise RuntimeError(f"Unknown alignment '{a}'.")

    lines = [
      f"|{'|'.join(header)}|",
      f"|{'|'.join(align_map[a] for a in alignment)}|",
      *[f"|{'|'.join(row)}|" for row in zip(*data)],
    ]
    return "\n".join(lines)

  @staticmethod
  def hrule() -> str:
    """Returns a Markdown horizontal rule."""
    return "---"

  @staticmethod
  def replace_section(content: str, marker: str, replacement: str) -> str:
    """Replaces text between <!-- START_{marker} --> and <!-- END_{marker} -->."""
    start_tag = f"<!-- START_{marker} -->"
    end_tag = f"<!-- END_{marker} -->"
    pattern = re.compile(
      rf"({re.escape(start_tag)}\n).*?(\n{re.escape(end_tag)})",
      re.DOTALL,
    )
    if not pattern.search(content):
      raise RuntimeError(
        f"Markers {start_tag} ... {end_tag} not found in README.md."
      )
    return pattern.sub(lambda m: f"{m.group(1)}{replacement}{m.group(2)}", content)
