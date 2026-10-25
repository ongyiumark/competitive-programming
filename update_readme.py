"""Updates the auto-generated sections of README.md from contest solutions."""

import os
from typing import Callable

from update_links import update_cache
from utils import (
  ATCODER_DOMAIN,
  ATCODER_PATH,
  CODEFORCES_DOMAIN,
  CODEFORCES_PATH,
  Contest,
  Markdown,
  is_solution_file,
  parse_solution_filename,
)

README_PATH = "README.md"


def count_tasks(directory: str) -> int:
  """Returns the number of unique solved tasks in the directory tree."""
  if not os.path.isdir(directory):
    return 0

  total = 0
  for _, _, filenames in os.walk(directory):
    tasks = {
      parse_solution_filename(name)[1]
      for name in filenames
      if is_solution_file(name)
    }
    total += len(tasks)
  return total


def get_missing_tasks(
  path: str,
  contests: dict[str, Contest],
) -> list[str]:
  """Returns unsolved task codes for a contest folder in canonical order."""
  contest_code = os.path.basename(path)
  if contest_code not in contests:
    return []

  tasks_solved = {
    parse_solution_filename(file)[1]
    for file in os.listdir(path)
    if os.path.isfile(os.path.join(path, file)) and is_solution_file(file)
  }

  return [
    task.task_code
    for task in contests[contest_code].tasks
    if task.task_code not in tasks_solved
  ]


def get_missing_tasks_from_dir(
  directory: str,
  contests: dict[str, Contest],
) -> list[tuple[str, list[str]]]:
  """Returns sorted (contest_code, missing_task_codes) pairs under directory."""
  if not os.path.isdir(directory):
    return []

  missing_by_contest = []
  for dirpath, _, filenames in os.walk(directory):
    if not any(is_solution_file(f) for f in filenames):
      continue

    contest_code = os.path.basename(dirpath)
    missing_tasks = get_missing_tasks(dirpath, contests)
    if missing_tasks:
      missing_by_contest.append((contest_code, missing_tasks))

  missing_by_contest.sort(key=lambda item: item[0])
  return missing_by_contest


def dir_to_collapsed_section(
  directory: str,
  start_level: int,
  file_parser: Callable[[str], str],
) -> str:
  """Recursively generates nested <details> sections for a directory tree."""
  def traverse(path: str, level: int) -> str:
    entries = sorted(os.listdir(path))

    lines = []
    for entry in entries:
      if entry.startswith("."):
        continue
      full_path = os.path.join(path, entry)
      if os.path.isdir(full_path):
        sub_section = traverse(full_path, level + 1)
        if sub_section:
          lines.extend(sub_section.split("\n"))
      elif is_solution_file(entry):
        lines.append(f"- {file_parser(full_path)}")

    if not lines:
      return ""

    if level < start_level:
      return "\n".join(lines)

    return Markdown.collapsed_section(
      summary=file_parser(path),
      lines=lines,
    )

  return traverse(directory, 0)


def format_entry(
  path: str,
  base_link: str,
  contests: dict[str, Contest],
) -> str:
  """Formats a solution file or contest directory for Markdown output."""
  if os.path.isfile(path):
    filename = os.path.basename(path)
    contest_code, task_code = parse_solution_filename(filename)

    contest = contests[contest_code]
    task_map = {t.task_code: t for t in contest.tasks}
    task = task_map[task_code]

    normalized_path = path.replace(os.sep, "/").replace(" ", "%20")
    relative_link = f"/{normalized_path}"
    filename_md = Markdown.link(text=filename, href=relative_link)
    taskname_md = Markdown.link(
      text=task.task_name,
      href=f"{base_link}{task.task_link}",
    )
    return f"{filename_md} - {taskname_md}"

  dirname = os.path.basename(path)
  if dirname in contests:
    return f"{dirname} - {contests[dirname].contest_name}"
  return dirname


def build_stats_table(target_folders: list[str]) -> str:
  """Generates the solved problems summary table."""
  return Markdown.table(
    header=["Category", "Number Solved"],
    alignment=["c", "c"],
    data=[
      target_folders,
      [str(count_tasks(path)) for path in target_folders],
    ],
  )


def build_all_problems_section(
  targets: list[tuple[str, str]],
  contests: dict[str, Contest],
) -> str:
  """Generates the collapsible tree of all solved problems."""
  collapsed_sections = []
  for path, base_link in targets:
    if not os.path.isdir(path):
      continue
    section = dir_to_collapsed_section(
      path,
      start_level=0,
      file_parser=lambda x, bl=base_link: format_entry(x, bl, contests),
    )
    if section:
      collapsed_sections.append(section)

  return "\n".join(collapsed_sections)


def build_missing_problems_section(
  targets: list[tuple[str, str]],
  contests: dict[str, Contest],
) -> str:
  """Generates the collapsible list of remaining tasks to upsolve."""
  contest_sections = []
  for path, base_link in targets:
    missing_by_contest = get_missing_tasks_from_dir(path, contests)
    for contest_code, task_codes in missing_by_contest:
      contest = contests[contest_code]
      task_map = {t.task_code: t for t in contest.tasks}

      task_lines = []
      for task_code in task_codes:
        task = task_map[task_code]
        task_md = Markdown.link(
          text=task.task_name,
          href=f"{base_link}{task.task_link}",
        )
        task_lines.append(f"- {task_code} - {task_md}")

      contest_sections.append(
        Markdown.collapsed_section(
          summary=f"{contest_code} - {contest.contest_name}",
          lines=task_lines,
        )
      )

  if not contest_sections:
    return "_Nothing left to upsolve!_"

  return "\n".join(contest_sections)


def main() -> None:
  """Updates contest cache and refreshes auto-generated sections in README.md."""
  contests = update_cache()

  target_folders = [ATCODER_PATH, CODEFORCES_PATH]
  target_domains = [ATCODER_DOMAIN, CODEFORCES_DOMAIN]
  targets = list(zip(target_folders, target_domains))

  with open(README_PATH, "r", encoding="utf-8") as f:
    original_readme = f.read()

  updated_readme = original_readme
  updated_readme = Markdown.replace_section(
    updated_readme,
    "STATS",
    build_stats_table(target_folders),
  )
  updated_readme = Markdown.replace_section(
    updated_readme,
    "ALL_PROBLEMS",
    build_all_problems_section(targets, contests),
  )
  updated_readme = Markdown.replace_section(
    updated_readme,
    "UPSOLVE",
    build_missing_problems_section(targets, contests),
  )

  if updated_readme != original_readme:
    with open(README_PATH, "w", encoding="utf-8") as f:
      f.write(updated_readme)
    print(f"Updated {README_PATH}.")
  else:
    print(f"{README_PATH} is already up to date.")


if __name__ == "__main__":
  main()
