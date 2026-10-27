"""Unit tests for tools/scaffold.py."""

import unittest

from tools.scaffold import (
  CPP_TEMPLATE,
  PYTHON_TEMPLATE,
  get_atcoder_path,
  get_codeforces_path,
)


class TestScaffold(unittest.TestCase):

  def test_get_atcoder_path(self):
    self.assertEqual(get_atcoder_path("ABC450"), "AtCoder/ABC 400-499/ABC450")
    self.assertEqual(get_atcoder_path("abc450"), "AtCoder/ABC 400-499/ABC450")
    self.assertEqual(get_atcoder_path("ABC050"), "AtCoder/ABC 0-99/ABC050")

    with self.assertRaises(ValueError):
      get_atcoder_path("../../traversal")

  def test_get_codeforces_path(self):
    dest, code, cid = get_codeforces_path("2220", "2")
    self.assertEqual(dest, "Codeforces/Contests/Division 2/CFC2220")
    self.assertEqual(code, "CFC2220")
    self.assertEqual(cid, "2220")

    # Handles cfc prefix and division names
    dest2, code2, cid2 = get_codeforces_path("cfc2220", "div2")
    self.assertEqual(dest2, "Codeforces/Contests/Division 2/CFC2220")
    self.assertEqual(code2, "CFC2220")
    self.assertEqual(cid2, "2220")

    with self.assertRaises(ValueError):
      get_codeforces_path("../../evil", "2")

  def test_templates_formatting(self):
    cpp_rendered = CPP_TEMPLATE.format(url="https://example.com/test")
    self.assertIn("https://example.com/test", cpp_rendered)
    self.assertIn("#include <cstdint>", cpp_rendered)
    self.assertIn("int main() {", cpp_rendered)

    py_rendered = PYTHON_TEMPLATE.format(url="https://example.com/test")
    self.assertIn("https://example.com/test", py_rendered)
    self.assertIn("def solve():", py_rendered)


if __name__ == "__main__":
  unittest.main()
