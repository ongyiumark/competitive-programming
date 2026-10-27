"""Fetches and caches contest metadata from AtCoder and Codeforces."""

import json
import os

from bs4 import BeautifulSoup
import requests

from utils import (
  ATCODER_PATH,
  CODEFORCES_PATH,
  CONTESTS_CACHE,
  Contest,
  Task,
  is_solution_file,
  natural_sort_key,
)

REQUEST_TIMEOUT = 10
USER_AGENT = (
  "Mozilla/5.0 (compatible; competitive-programming-updater/2.0; "
  "+https://github.com/ongyiumark/competitive-programming)"
)


def get_contest_codes_from_directory(directory: str) -> list[str]:
  """Returns sorted contest directory names that contain solution files."""
  if not os.path.isdir(directory):
    return []

  contest_codes = []
  for dirpath, _, filenames in os.walk(directory):
    solution_files = [f for f in filenames if is_solution_file(f)]
    if not solution_files:
      continue
    contest_codes.append(os.path.basename(dirpath))

  return sorted(set(contest_codes), key=natural_sort_key)


def get_atcoder_contest_details(contest_code: str) -> Contest:
  """Scrapes contest title and task list from an AtCoder contest tasks page."""
  task_url = f"https://atcoder.jp/contests/{contest_code}/tasks"
  response = requests.get(
    task_url,
    headers={"User-Agent": USER_AGENT},
    timeout=REQUEST_TIMEOUT,
  )
  if response.status_code != 200:
    raise RuntimeError(
      f"Failed to get {task_url}. Status code {response.status_code}."
    )

  soup = BeautifulSoup(response.text, features="html.parser")
  contest_title_tag = soup.find(class_="contest-title")
  if contest_title_tag is None:
    raise RuntimeError(f"Could not find contest title on {task_url}.")

  contest_name = contest_title_tag.text.strip()
  canonical_code = contest_title_tag.get("href", "").rsplit("/", 1)[-1].upper()
  code = canonical_code or contest_code.upper()

  contest = Contest(contest_code=code, contest_name=contest_name)
  panel = soup.find("div", class_="panel")
  tbody = panel.find("tbody") if panel else None
  if tbody is None:
    raise RuntimeError(f"Could not find tasks table on {task_url}.")

  for row in tbody.find_all("tr"):
    cells = row.find_all("td")
    if len(cells) < 2:
      continue
    task_code = cells[0].text.strip()
    task_name = cells[1].text.strip()
    link_tag = cells[0].find("a")
    task_link = link_tag.get("href") if link_tag else (
      f"/contests/{code}/tasks/{code.lower()}_{task_code.lower()}"
    )
    contest.add_task(
      Task(task_code=task_code, task_name=task_name, task_link=task_link)
    )

  return contest


def get_codeforces_contest_details(
  contest_id: str,
  prefix: str = "CFC",
) -> Contest:
  """Fetches contest details from the official Codeforces API."""
  api_url = (
    f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=1"
  )
  response = requests.get(
    api_url,
    headers={"User-Agent": USER_AGENT},
    timeout=REQUEST_TIMEOUT,
  )
  if response.status_code != 200:
    detail = f"HTTP {response.status_code}"
    try:
      comment = response.json().get("comment")
      if comment:
        detail = f"{detail} - {comment}"
    except ValueError:
      pass
    raise RuntimeError(
      f"Failed to query Codeforces API for contest {contest_id} ({detail})."
    )

  payload = response.json()
  if payload.get("status") != "OK":
    comment = payload.get("comment", "Unknown API error")
    raise RuntimeError(
      f"Codeforces API error for contest {contest_id}: {comment}"
    )

  result = payload["result"]
  contest_name = result["contest"]["name"].strip()
  contest = Contest(
    contest_code=f"{prefix}{contest_id}",
    contest_name=contest_name,
  )

  for problem in result.get("problems", []):
    task_code = str(problem["index"]).strip()
    task_name = str(problem["name"]).strip()
    task_link = f"/contest/{contest_id}/problem/{task_code}"
    contest.add_task(
      Task(task_code=task_code, task_name=task_name, task_link=task_link)
    )

  return contest


def load_cache(cache_path: str = CONTESTS_CACHE) -> dict[str, Contest]:
  """Loads cached contest metadata from JSON."""
  if not os.path.exists(cache_path):
    return {}

  with open(cache_path, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

  return {
    code: Contest.from_dict(code, data)
    for code, data in raw_data.items()
  }


def save_cache(
  contests: dict[str, Contest],
  cache_path: str = CONTESTS_CACHE,
) -> None:
  """Writes cached contest metadata to JSON sorted by contest code."""
  os.makedirs(os.path.dirname(cache_path), exist_ok=True)
  serialized = {
    code: contests[code].to_dict()
    for code in sorted(contests.keys(), key=natural_sort_key)
  }
  with open(cache_path, "w", encoding="utf-8") as f:
    json.dump(serialized, f, indent=2, ensure_ascii=False)
    f.write("\n")


def update_cache(cache_path: str = CONTESTS_CACHE) -> dict[str, Contest]:
  """Fetches any uncached contests found in target directories and updates cache."""
  contests = load_cache(cache_path)
  updated = False

  atcoder_codes = get_contest_codes_from_directory(ATCODER_PATH)
  missing_atcoder = [code for code in atcoder_codes if code not in contests]
  for code in missing_atcoder:
    print(f"Fetching AtCoder contest '{code}'...")
    contest = get_atcoder_contest_details(code)
    contests[contest.contest_code] = contest
    updated = True

  codeforces_codes = get_contest_codes_from_directory(CODEFORCES_PATH)
  missing_cf = [
    code for code in codeforces_codes
    if code.startswith("CFC") and code not in contests
  ]
  for code in missing_cf:
    contest_id = code[3:]
    print(f"Fetching Codeforces contest '{code}' via API...")
    contest = get_codeforces_contest_details(contest_id, prefix="CFC")
    contests[contest.contest_code] = contest
    updated = True

  if updated:
    save_cache(contests, cache_path)
    print(f"Updated cache at {cache_path}.")

  return contests


def main() -> None:
  """CLI entrypoint to refresh the contest cache."""
  update_cache()


if __name__ == "__main__":
  main()
