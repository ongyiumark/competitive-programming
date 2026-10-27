"""Unit tests for utils.py helper functions and data structures."""

import unittest

from utils import (
  Contest,
  Markdown,
  Task,
  is_solution_file,
  natural_sort_key,
  parse_solution_filename,
)


class TestUtils(unittest.TestCase):

  def test_is_solution_file(self):
    # Valid solution files
    self.assertTrue(is_solution_file("ABC450_A.py"))
    self.assertTrue(is_solution_file("ABC450_A.cpp"))
    self.assertTrue(is_solution_file("CFC2220_D1.cpp"))
    self.assertTrue(is_solution_file("ABC450_A_v2.cpp"))
    self.assertTrue(is_solution_file("abc450_a.py"))

    # Invalid files
    self.assertFalse(is_solution_file(".DS_Store"))
    self.assertFalse(is_solution_file(".gitignore"))
    self.assertFalse(is_solution_file("solution.cpp"))
    self.assertFalse(is_solution_file("_test.py"))
    self.assertFalse(is_solution_file("test_.py"))
    self.assertFalse(is_solution_file("README.md"))
    self.assertFalse(is_solution_file("contests.json"))

  def test_parse_solution_filename(self):
    self.assertEqual(parse_solution_filename("ABC450_A.py"), ("ABC450", "A"))
    self.assertEqual(parse_solution_filename("abc450_a.cpp"), ("ABC450", "A"))
    self.assertEqual(parse_solution_filename("CFC2220_D1.cpp"), ("CFC2220", "D1"))
    self.assertEqual(parse_solution_filename("ABC450_A_v2.cpp"), ("ABC450", "A"))

  def test_natural_sort_key(self):
    contest_codes = ["ABC100", "ABC9", "ABC10", "ABC2"]
    sorted_codes = sorted(contest_codes, key=natural_sort_key)
    self.assertEqual(sorted_codes, ["ABC2", "ABC9", "ABC10", "ABC100"])

    cf_codes = ["CFC2220", "CFC999", "CFC1000"]
    self.assertEqual(
      sorted(cf_codes, key=natural_sort_key),
      ["CFC999", "CFC1000", "CFC2220"],
    )

  def test_contest_serialization(self):
    contest = Contest(
      contest_code="ABC450",
      contest_name="AtCoder Beginner Contest 450",
    )
    contest.add_task(
      Task(task_code="A", task_name="3,2,1,GO", task_link="/tasks/abc450_a")
    )

    data = contest.to_dict()
    self.assertEqual(data["name"], "AtCoder Beginner Contest 450")
    self.assertIn("A", data["tasks"])

    restored = Contest.from_dict("ABC450", data)
    self.assertEqual(restored.contest_code, "ABC450")
    self.assertEqual(restored.contest_name, contest.contest_name)
    self.assertEqual(len(restored.tasks), 1)
    self.assertEqual(restored.tasks[0].task_name, "3,2,1,GO")

  def test_markdown_replace_section(self):
    original = "Intro\n<!-- START_TEST -->\nOld content\n<!-- END_TEST -->\nOutro"
    updated = Markdown.replace_section(original, "TEST", "New content")
    expected = "Intro\n<!-- START_TEST -->\nNew content\n<!-- END_TEST -->\nOutro"
    self.assertEqual(updated, expected)

    with self.assertRaises(RuntimeError):
      Markdown.replace_section(original, "NONEXISTENT", "New content")

  def test_markdown_table(self):
    table = Markdown.table(
      header=["Col1", "Col2"],
      alignment=["l", "c"],
      data=[["a", "b"], ["1", "2"]],
    )
    expected = "|Col1|Col2|\n|:-|:-:|\n|a|1|\n|b|2|"
    self.assertEqual(table, expected)


if __name__ == "__main__":
  unittest.main()
