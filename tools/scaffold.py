"""Scaffolds new contest directories and starter solution files."""

import argparse
import os
import re

CPP_TEMPLATE = """\
/* {url} */
#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>

using namespace std;
typedef int64_t ll;
typedef long double ld;
typedef vector<int> vi;
typedef vector<ll> vll;

int main() {{
  ios_base::sync_with_stdio(false);
  cin.tie(NULL);

  return 0;
}}
"""

PYTHON_TEMPLATE = """\
\"\"\"{url}\"\"\"
import sys


def solve():
  input = sys.stdin.readline
  # TODO


if __name__ == "__main__":
  solve()
"""


def get_atcoder_path(contest_code: str) -> str:
  code = contest_code.strip().upper()
  if not re.match(r"^[A-Z0-9_-]+$", code):
    raise ValueError(f"Invalid AtCoder contest code: {contest_code!r}")

  match = re.match(r"^([A-Z]+)(\d+)$", code)
  if match:
    prefix, num_str = match.groups()
    num = int(num_str)
    lower = (num // 100) * 100
    upper = lower + 99
    group_name = f"{prefix} {lower}-{upper}"
    return os.path.join("AtCoder", group_name, code)
  return os.path.join("AtCoder", code)


def get_codeforces_path(contest_id: str, division: str) -> tuple[str, str, str]:
  cid = str(contest_id).strip().upper()
  clean_id = cid[3:] if cid.startswith("CFC") else cid
  if not re.match(r"^[A-Z0-9_-]+$", clean_id):
    raise ValueError(f"Invalid Codeforces contest ID: {contest_id!r}")
  contest_code = f"CFC{clean_id}"

  div_clean = re.sub(
    r"^(?:div(?:ision)?\.?\s*)",
    "",
    str(division).strip(),
    flags=re.IGNORECASE,
  )
  div_name = f"Division {div_clean}" if div_clean else ""
  dest_dir = (
    os.path.join("Codeforces", "Contests", div_name, contest_code)
    if div_name
    else os.path.join("Codeforces", "Contests", contest_code)
  )
  return dest_dir, contest_code, clean_id


def scaffold_atcoder(args: argparse.Namespace) -> None:
  code = args.contest.strip().upper()
  tasks = args.tasks or ["A", "B", "C", "D", "E", "F", "G"]
  dest_dir = get_atcoder_path(code)
  os.makedirs(dest_dir, exist_ok=True)
  ext = ".py" if args.lang == "py" else ".cpp"

  for task in tasks:
    task_clean = str(task).strip().upper()
    if not re.match(r"^[A-Z0-9_-]+$", task_clean):
      raise ValueError(f"Invalid task code: {task!r}")

    filename = f"{code}_{task_clean}{ext}"
    filepath = os.path.join(dest_dir, filename)
    if os.path.exists(filepath):
      print(f"Skipping existing: {filepath}")
      continue

    url = (
      f"https://atcoder.jp/contests/{code.lower()}/tasks/"
      f"{code.lower()}_{task_clean.lower()}"
    )
    content = (
      PYTHON_TEMPLATE.format(url=url)
      if args.lang == "py"
      else CPP_TEMPLATE.format(url=url)
    )

    with open(filepath, "w", encoding="utf-8") as f:
      f.write(content)
    print(f"Created {filepath}")


def scaffold_codeforces(args: argparse.Namespace) -> None:
  dest_dir, contest_code, clean_id = get_codeforces_path(args.contest, args.div)
  tasks = args.tasks or ["A", "B", "C", "D", "E", "F"]
  os.makedirs(dest_dir, exist_ok=True)
  ext = ".py" if args.lang == "py" else ".cpp"

  for task in tasks:
    task_clean = str(task).strip().upper()
    if not re.match(r"^[A-Z0-9_-]+$", task_clean):
      raise ValueError(f"Invalid task code: {task!r}")

    filename = f"{contest_code}_{task_clean}{ext}"
    filepath = os.path.join(dest_dir, filename)
    if os.path.exists(filepath):
      print(f"Skipping existing: {filepath}")
      continue

    url = f"https://codeforces.com/contest/{clean_id}/problem/{task_clean}"
    content = (
      PYTHON_TEMPLATE.format(url=url)
      if args.lang == "py"
      else CPP_TEMPLATE.format(url=url)
    )

    with open(filepath, "w", encoding="utf-8") as f:
      f.write(content)
    print(f"Created {filepath}")


def main() -> None:
  parser = argparse.ArgumentParser(description="Scaffold competitive programming contests.")
  subparsers = parser.add_subparsers(dest="platform", required=True)

  # AtCoder parser
  ac_parser = subparsers.add_parser("atcoder", aliases=["ac"], help="Scaffold AtCoder contest")
  ac_parser.add_argument("contest", help="Contest code, e.g. ABC479")
  ac_parser.add_argument("--tasks", nargs="+", help="Task codes (defaults to A-G)")
  ac_parser.add_argument("--lang", choices=["cpp", "py"], default="cpp", help="Language (default: cpp)")
  ac_parser.set_defaults(func=scaffold_atcoder)

  # Codeforces parser
  cf_parser = subparsers.add_parser("codeforces", aliases=["cf"], help="Scaffold Codeforces contest")
  cf_parser.add_argument("contest", help="Contest ID, e.g. 2221 or CFC2221")
  cf_parser.add_argument("--div", default="2", help="Division (e.g. 1, 2, 3, 4; default: 2)")
  cf_parser.add_argument("--tasks", nargs="+", help="Task codes (defaults to A-F)")
  cf_parser.add_argument("--lang", choices=["cpp", "py"], default="cpp", help="Language (default: cpp)")
  cf_parser.set_defaults(func=scaffold_codeforces)

  args = parser.parse_args()
  args.func(args)


if __name__ == "__main__":
  main()
