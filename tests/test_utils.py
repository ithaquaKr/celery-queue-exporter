from exporter.utils import parse_monitor_queues


def test_parse_monitor_queues_valid_string():
    config = "0:celery;1:task,cache"
    expected = {0: ["celery"], 1: ["cache", "task"]}
    assert parse_monitor_queues(config) == expected


def test_parse_monitor_queues_empty_string():
    config = ""
    expected = {}
    assert parse_monitor_queues(config) == expected


def test_parse_monitor_queues_with_spaces():
    config = " 0 : celery ; 1 : task , cache "
    expected = {0: ["celery"], 1: ["cache", "task"]}
    assert parse_monitor_queues(config) == expected


def test_parse_monitor_queues_duplicate_queues():
    config = "0:celery;0:celery"
    expected = {0: ["celery"]}
    assert parse_monitor_queues(config) == expected


def test_parse_monitor_queues_multiple_queues_for_db():
    config = "0:celery;1:task,cache;1:extra_queue"
    expected = {0: ["celery"], 1: ["cache", "extra_queue", "task"]}
    assert parse_monitor_queues(config) == expected


def test_parse_monitor_queues_malformed_entries():
    config = "0:celery;1;2:task"
    expected = {0: ["celery"], 2: ["task"]}
    assert parse_monitor_queues(config) == expected


def test_parse_monitor_queues_empty_queue_names():
    config = "0:celery;1:;2:task"
    expected = {0: ["celery"], 2: ["task"]}
    assert parse_monitor_queues(config) == expected


def test_parse_monitor_queues_single_entry():
    config = "0:celery"
    expected = {0: ["celery"]}
    assert parse_monitor_queues(config) == expected


def test_parse_monitor_queues_complex_string():
    config = "0:celery;1:task,cache;1:extra_queue;2:another_queue"
    expected = {
        0: ["celery"],
        1: ["cache", "extra_queue", "task"],
        2: ["another_queue"],
    }
    assert parse_monitor_queues(config) == expected


def test_parse_monitor_queues_no_db():
    config = ":celery"
    expected = {}
    assert parse_monitor_queues(config) == expected


def test_parse_monitor_queues_no_queue():
    config = "0:"
    expected = {}
    assert parse_monitor_queues(config) == expected
