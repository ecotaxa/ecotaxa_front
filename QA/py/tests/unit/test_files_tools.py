from appli.gui.files.tools import _dedupe_nested_entries, _unique_staged_name


def test_dedupe_keeps_top_most_entries():
    entries = ["a/b/c.zip", "a/b", "/a/b/", "x.tsv", "ab/c", "", "  ", None]
    assert _dedupe_nested_entries(entries) == ["a/b", "ab/c", "x.tsv"] or sorted(
        _dedupe_nested_entries(entries)
    ) == ["a/b", "ab/c", "x.tsv"]


def test_dedupe_prefix_is_not_ancestor():
    # "ab" is not a parent of "abc/d"
    assert sorted(_dedupe_nested_entries(["ab", "abc/d"])) == ["ab", "abc/d"]


def test_unique_staged_name_suffixes():
    used: set = set()
    assert _unique_staged_name("data.zip", used) == "data.zip"
    assert _unique_staged_name("data.zip", used) == "data_2.zip"
    assert _unique_staged_name("data.zip", used) == "data_3.zip"
    assert _unique_staged_name("dir", used) == "dir"
    assert _unique_staged_name("dir", used) == "dir_2"
    assert used == {"data.zip", "data_2.zip", "data_3.zip", "dir", "dir_2"}
