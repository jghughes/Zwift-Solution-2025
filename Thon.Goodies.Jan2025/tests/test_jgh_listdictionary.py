import pytest

from jgh_listdictionary import JghListDictionary


@pytest.fixture
def populated() -> JghListDictionary[str, int]:
    d = JghListDictionary[str, int]()
    for value in (1, 2, 2, 3):
        d.append_value_to_list("a", value)
    for value in (3, 4):
        d.append_value_to_list("b", value)
    d.insert_key("empty")
    return d


@pytest.fixture
def nullable() -> JghListDictionary[str | None, int | None]:
    return JghListDictionary[str | None, int | None]()


# --- construction and isolation ---


def test_new_instance_is_empty() -> None:
    d = JghListDictionary[str, int]()

    assert d.count_of_keys == 0
    assert d.count_of_values == 0
    assert d.get_keys() == []


def test_instances_do_not_share_storage() -> None:
    first = JghListDictionary[str, int]()
    second = JghListDictionary[str, int]()

    first.append_value_to_list("a", 1)

    assert second.count_of_keys == 0


# --- insert_key ---


def test_insert_key_adds_new_key_with_empty_list() -> None:
    d = JghListDictionary[str, int]()

    assert d.insert_key("a") is True
    assert d.get_keys() == ["a"]
    assert d.get_values("a") == []


def test_insert_key_returns_false_and_preserves_values_when_key_exists(
    populated: JghListDictionary[str, int],
) -> None:
    assert populated.insert_key("a") is False
    assert populated.get_values("a") == [1, 2, 2, 3]


def test_insert_key_rejects_none(nullable: JghListDictionary[str | None, int | None]) -> None:
    assert nullable.insert_key(None) is False
    assert nullable.count_of_keys == 0


# --- remove_key ---


def test_remove_key_returns_values_and_removes_key(populated: JghListDictionary[str, int]) -> None:
    assert populated.remove_key("b") == [3, 4]
    assert not populated.contains_key("b")


@pytest.mark.parametrize("key", ["missing", None])
def test_remove_key_returns_empty_list_for_missing_or_none_key(
    nullable: JghListDictionary[str | None, int | None], key: str | None
) -> None:
    nullable.append_value_to_list("a", 1)

    assert nullable.remove_key(key) == []
    assert nullable.get_keys() == ["a"]


# --- append_value_to_list ---


def test_append_value_creates_key_and_keeps_duplicates() -> None:
    d = JghListDictionary[str, int]()

    d.append_value_to_list("a", 1)
    d.append_value_to_list("a", 1)

    assert d.get_values("a") == [1, 1]


@pytest.mark.parametrize(("key", "value"), [(None, 1), ("a", None), (None, None)])
def test_append_value_ignores_none_key_or_value(
    nullable: JghListDictionary[str | None, int | None], key: str | None, value: int | None
) -> None:
    nullable.append_value_to_list(key, value)

    assert nullable.count_of_keys == 0
    assert nullable.count_of_values == 0


# --- remove_value_from_list ---


def test_remove_value_from_list_removes_all_occurrences(populated: JghListDictionary[str, int]) -> None:
    assert populated.remove_value_from_list("a", 2) == 2
    assert populated.get_values("a") == [1, 3]


def test_remove_value_from_list_keeps_the_key_when_list_becomes_empty() -> None:
    d = JghListDictionary[str, int]()
    d.append_value_to_list("a", 1)

    assert d.remove_value_from_list("a", 1) == 1
    assert d.contains_key("a")
    assert d.get_values("a") == []


def test_remove_value_from_list_returns_zero_for_absent_value(populated: JghListDictionary[str, int]) -> None:
    assert populated.remove_value_from_list("a", 99) == 0
    assert populated.get_values("a") == [1, 2, 2, 3]


def test_remove_value_from_list_does_not_create_missing_key(populated: JghListDictionary[str, int]) -> None:
    assert populated.remove_value_from_list("missing", 1) == 0
    assert not populated.contains_key("missing")


@pytest.mark.parametrize(("key", "value"), [(None, 1), ("a", None)])
def test_remove_value_from_list_returns_zero_for_none(
    nullable: JghListDictionary[str | None, int | None], key: str | None, value: int | None
) -> None:
    nullable.append_value_to_list("a", 1)

    assert nullable.remove_value_from_list(key, value) == 0
    assert nullable.get_values("a") == [1]


# --- remove_value_from_all_lists ---


def test_remove_value_from_all_lists_reports_count_and_keys(populated: JghListDictionary[str, int]) -> None:
    count, keys = populated.remove_value_from_all_lists(3)

    assert count == 2
    assert sorted(keys) == ["a", "b"]
    assert populated.get_values("a") == [1, 2, 2]
    assert populated.get_values("b") == [4]


def test_remove_value_from_all_lists_counts_repeats_within_a_list(populated: JghListDictionary[str, int]) -> None:
    assert populated.remove_value_from_all_lists(2) == (2, ["a"])


def test_remove_value_from_all_lists_returns_nothing_for_absent_value(populated: JghListDictionary[str, int]) -> None:
    assert populated.remove_value_from_all_lists(99) == (0, [])


def test_remove_value_from_all_lists_returns_nothing_for_none(
    nullable: JghListDictionary[str | None, int | None],
) -> None:
    nullable.append_value_to_list("a", 1)

    assert nullable.remove_value_from_all_lists(None) == (0, [])


def test_remove_value_from_all_lists_on_empty_dictionary() -> None:
    assert JghListDictionary[str, int]().remove_value_from_all_lists(1) == (0, [])


# --- deduplicate_values_per_list ---


def test_deduplicate_keeps_first_occurrence_and_order(populated: JghListDictionary[str, int]) -> None:
    populated.deduplicate_values_per_list()

    assert populated.get_values("a") == [1, 2, 3]
    assert populated.get_values("b") == [3, 4]


def test_deduplicate_only_works_within_each_list(populated: JghListDictionary[str, int]) -> None:
    populated.deduplicate_values_per_list()

    assert populated.contains_value_in_list("a", 3)
    assert populated.contains_value_in_list("b", 3)


def test_deduplicate_keeps_keys_and_supports_unhashable_values() -> None:
    d = JghListDictionary[str, list[int]]()
    d.append_value_to_list("a", [1])
    d.append_value_to_list("a", [1])
    d.insert_key("empty")

    d.deduplicate_values_per_list()

    assert d.get_values("a") == [[1]]
    assert d.contains_key("empty")


# --- clear_all_values_from_list / clear_everything_everywhere ---


def test_clear_all_values_from_list_empties_list_and_keeps_key(populated: JghListDictionary[str, int]) -> None:
    assert populated.clear_all_values_from_list("a") == 4
    assert populated.contains_key("a")
    assert populated.get_value_count_for_key("a") == 0


def test_clear_all_values_from_list_returns_zero_for_missing_key(populated: JghListDictionary[str, int]) -> None:
    assert populated.clear_all_values_from_list("missing") == 0
    assert not populated.contains_key("missing")


def test_clear_all_values_from_list_returns_zero_for_none(
    nullable: JghListDictionary[str | None, int | None],
) -> None:
    assert nullable.clear_all_values_from_list(None) == 0


def test_clear_everything_everywhere_returns_original_counts(populated: JghListDictionary[str, int]) -> None:
    assert populated.clear_everything_everywhere() == (3, 6)
    assert populated.count_of_keys == 0
    assert populated.count_of_values == 0


# --- contains_* ---


def test_contains_key(populated: JghListDictionary[str, int]) -> None:
    assert populated.contains_key("a")
    assert populated.contains_key("empty")
    assert not populated.contains_key("missing")


def test_contains_key_does_not_add_the_key(populated: JghListDictionary[str, int]) -> None:
    populated.contains_key("missing")

    assert populated.count_of_keys == 3


def test_contains_value_in_list(populated: JghListDictionary[str, int]) -> None:
    assert populated.contains_value_in_list("a", 2)
    assert not populated.contains_value_in_list("a", 4)
    assert not populated.contains_value_in_list("missing", 1)
    assert not populated.contains_key("missing")


@pytest.mark.parametrize(("key", "value"), [(None, 1), ("a", None)])
def test_contains_value_in_list_is_false_for_none(
    nullable: JghListDictionary[str | None, int | None], key: str | None, value: int | None
) -> None:
    nullable.append_value_to_list("a", 1)

    assert not nullable.contains_value_in_list(key, value)


def test_contains_value_in_any_list(populated: JghListDictionary[str, int]) -> None:
    assert populated.contains_value_in_any_list(4)
    assert not populated.contains_value_in_any_list(99)


def test_contains_value_in_any_list_is_false_for_none(
    nullable: JghListDictionary[str | None, int | None],
) -> None:
    nullable.append_value_to_list("a", 1)

    assert not nullable.contains_value_in_any_list(None)


# --- key queries ---


def test_get_keys_preserves_insertion_order(populated: JghListDictionary[str, int]) -> None:
    assert populated.get_keys() == ["a", "b", "empty"]


def test_get_keys_containing_value_lists_each_key_once(populated: JghListDictionary[str, int]) -> None:
    assert populated.get_keys_containing_value(2) == ["a"]
    assert populated.get_keys_containing_value(3) == ["a", "b"]
    assert populated.get_keys_containing_value(99) == []


def test_get_keys_containing_selected_values(populated: JghListDictionary[str, int]) -> None:
    assert populated.get_keys_containing_selected_values(lambda v: v >= 4) == ["b"]
    assert populated.get_keys_containing_selected_values(lambda v: v == 3) == ["a", "b"]
    assert populated.get_keys_containing_selected_values(lambda v: v > 100) == []


# --- value queries ---


def test_get_value_count_for_key(populated: JghListDictionary[str, int]) -> None:
    assert populated.get_value_count_for_key("a") == 4
    assert populated.get_value_count_for_key("empty") == 0
    assert populated.get_value_count_for_key("missing") == 0
    assert not populated.contains_key("missing")


def test_get_value_count_for_key_is_zero_for_none(
    nullable: JghListDictionary[str | None, int | None],
) -> None:
    assert nullable.get_value_count_for_key(None) == 0


def test_get_values_returns_a_copy(populated: JghListDictionary[str, int]) -> None:
    populated.get_values("a").append(99)

    assert populated.get_values("a") == [1, 2, 2, 3]


def test_get_values_for_missing_key_is_empty_and_does_not_add_key(populated: JghListDictionary[str, int]) -> None:
    assert populated.get_values("missing") == []
    assert not populated.contains_key("missing")


def test_get_values_raises_for_none_key(nullable: JghListDictionary[str | None, int | None]) -> None:
    with pytest.raises(ValueError, match="key cannot be None"):
        nullable.get_values(None)


def test_get_values_for_keys_includes_repeats(populated: JghListDictionary[str, int]) -> None:
    assert populated.get_values_for_keys(lambda k: k == "a") == [1, 2, 2, 3]
    assert populated.get_values_for_keys(lambda k: k in {"a", "b"}) == [1, 2, 2, 3, 3, 4]
    assert populated.get_values_for_keys(lambda k: k == "nope") == []


def test_get_values_for_all_includes_repeats(populated: JghListDictionary[str, int]) -> None:
    assert populated.get_values_for_all() == [1, 2, 2, 3, 3, 4]


def test_get_selected_values_from_key(populated: JghListDictionary[str, int]) -> None:
    assert populated.get_selected_values_from_key("a", lambda v: v == 2) == [2, 2]
    assert populated.get_selected_values_from_key("missing", lambda _: True) == []
    assert not populated.contains_key("missing")


def test_get_selected_values_from_key_is_empty_for_none(
    nullable: JghListDictionary[str | None, int | None],
) -> None:
    assert nullable.get_selected_values_from_key(None, lambda _: True) == []


def test_get_selected_values_from_all(populated: JghListDictionary[str, int]) -> None:
    assert populated.get_selected_values_from_all(lambda v: v % 2 == 1) == [1, 3, 3]


# --- key/value pairs ---


def test_get_key_value_pairs_includes_every_occurrence(populated: JghListDictionary[str, int]) -> None:
    assert populated.get_key_value_pairs() == [("a", 1), ("a", 2), ("a", 2), ("a", 3), ("b", 3), ("b", 4)]


def test_get_key_value_pairs_containing_selected_values(populated: JghListDictionary[str, int]) -> None:
    assert populated.get_key_value_pairs_containing_selected_values(lambda v: v == 3) == [("a", 3), ("b", 3)]
    assert populated.get_key_value_pairs_containing_selected_values(lambda v: v > 100) == []


# --- counts ---


def test_counts_include_keys_with_empty_lists(populated: JghListDictionary[str, int]) -> None:
    assert populated.count_of_keys == 3
    assert populated.count_of_values == 6


# --- indexer ---


def test_getitem_returns_a_copy_and_never_adds_a_key(populated: JghListDictionary[str, int]) -> None:
    populated["a"].append(99)

    assert populated["a"] == [1, 2, 2, 3]
    assert populated["missing"] == []
    assert not populated.contains_key("missing")


def test_setitem_replaces_values_with_a_copy() -> None:
    d = JghListDictionary[str, int]()
    source = [1, 2]

    d["a"] = source
    source.append(3)

    assert d.get_values("a") == [1, 2]


def test_setitem_does_not_share_a_list_between_keys() -> None:
    d = JghListDictionary[str, int]()
    shared = [1]

    d["a"] = shared
    d["b"] = shared
    d.append_value_to_list("a", 2)

    assert d.get_values("b") == [1]
