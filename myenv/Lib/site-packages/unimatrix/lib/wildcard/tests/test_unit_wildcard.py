# pylint: skip-file
import pytest

from .. import matches


def test_matching_no_wilcard():
    assert matches(["foo"], ["foo", "bar", "baz", "baz.taz"]) == {"foo"}
    assert matches({"foo"}, ["foo", "bar", "baz", "baz.taz"]) == {"foo"}


def test_list_matching_with_wilcard():
    patterns = ["foo", "bar.*"]
    values = ["foo", "bar", "baz", "bar.taz", "foo.bar"]
    assert matches(patterns, values) == {"foo", "bar.taz"}


def test_list_matching_with_no_matches():
    assert matches([], ["foo"]) == set()
    assert matches(["bar"], ["foo"]) == set()
    assert matches(["bar.*"], ["foo"]) == set()
    assert matches(["foo", "bar.*"], ["foo.bar"]) == set()
