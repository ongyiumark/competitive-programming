"""Unit tests for update_readme.py logic."""

import os
import tempfile
import unittest

from update_readme import count_tasks, format_entry, get_missing_tasks
from utils import Contest, Task


class TestUpdateReadme(unittest.TestCase):

  def test_count_tasks(self):
    with tempfile.TemporaryDirectory() as tmpdir:
      c1 = os.path.join(tmpdir, "ABC450")
      os.makedirs(c1)
      with open(os.path.join(c1, "ABC450_A.cpp"), "w") as f:
        f.write("")
      with open(os.path.join(c1, "ABC450_A_v2.cpp"), "w") as f:
        f.write("")  # Same task code, should count once
      with open(os.path.join(c1, "ABC450_B.cpp"), "w") as f:
        f.write("")
      with open(os.path.join(c1, "ignored.txt"), "w") as f:
        f.write("")

      self.assertEqual(count_tasks(tmpdir), 2)

  def test_get_missing_tasks(self):
    contest = Contest(contest_code="ABC450", contest_name="ABC 450")
    contest.add_task(Task("A", "Task A", "/a"))
    contest.add_task(Task("B", "Task B", "/b"))
    contest.add_task(Task("C", "Task C", "/c"))
    contests = {"ABC450": contest}

    with tempfile.TemporaryDirectory() as tmpdir:
      c_dir = os.path.join(tmpdir, "ABC450")
      os.makedirs(c_dir)
      with open(os.path.join(c_dir, "ABC450_A.cpp"), "w") as f:
        f.write("")

      missing = get_missing_tasks(c_dir, contests)
      self.assertEqual(missing, ["B", "C"])

  def test_format_entry(self):
    contest = Contest(contest_code="ABC450", contest_name="ABC 450")
    contest.add_task(Task("A", "Task A", "/tasks/abc450_a"))
    contests = {"ABC450": contest}

    with tempfile.TemporaryDirectory() as tmpdir:
      fpath = os.path.join(tmpdir, "ABC450_A.cpp")
      with open(fpath, "w") as f:
        f.write("")

      entry = format_entry(fpath, "https://atcoder.jp", contests)
      self.assertIn("[ABC450_A.cpp]", entry)
      self.assertIn("[Task A](https://atcoder.jp/tasks/abc450_a)", entry)

      # Unrecognized task does not crash, returns filename link
      fpath_extra = os.path.join(tmpdir, "ABC450_Z.cpp")
      with open(fpath_extra, "w") as f:
        f.write("")
      entry_extra = format_entry(fpath_extra, "https://atcoder.jp", contests)
      expected_link = f"[{os.path.basename(fpath_extra)}](/{fpath_extra.replace(os.sep, '/')})"
      self.assertEqual(entry_extra, expected_link)


if __name__ == "__main__":
  unittest.main()
