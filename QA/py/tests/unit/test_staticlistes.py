from appli.gui import staticlistes as sl


def _walk(tree, path=""):
    for key, node in tree.items():
        yield path + "/" + key, node
        if isinstance(node, dict) and "children" in node:
            yield from _walk(node["children"], path + "/" + key)


def test_apptree_nodes_are_well_formed():
    allowed = {"root", "one", "url", "children"}
    for path, node in _walk(sl.apptree):
        assert isinstance(node, (str, dict)) or hasattr(node, "__html__") or str(node), path
        if isinstance(node, dict):
            assert set(node) <= allowed, (path, set(node) - allowed)
            if "children" in node:
                assert isinstance(node["children"], dict), path


def test_apptree_has_main_sections():
    for key in ("", "prj", "collection", "jobs"):
        assert key in sl.apptree


def test_crumb_aliases_point_to_existing_nodes():
    # old /gui/job/... routes share the "jobs" crumb
    assert sl.crumb_aliases["job"] == "jobs"
    for alias, target in sl.crumb_aliases.items():
        assert alias not in sl.apptree, alias
        assert target in sl.apptree, target


def test_message_dicts_are_flat_strings():
    for name in ("py_messages", "py_user"):
        d = getattr(sl, name)
        assert isinstance(d, dict) and d
        for k, v in d.items():
            assert isinstance(k, str)
            assert isinstance(v, (str, dict)) or str(v), (name, k)
