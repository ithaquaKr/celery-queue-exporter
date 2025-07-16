from typing import Dict, List


def parse_monitor_queues(mqs_config: str) -> Dict[int, List[str]]:
    """
    Parses a configuration string for monitoring queues into a dictionary.

    The configuration string format is a semicolon-separated list of database
    and queue definitions, e.g., "0:celery;1:task,cache;1:extra_queue".

    Args:
        config_string: The string containing the queue configuration.

    Returns:
        A dictionary where keys are database numbers (int) and values are
        lists of unique queue names (str).
        Returns an empty dictionary if the config string is empty or invalid.
    """
    if not mqs_config:
        return {}

    queue_dict: Dict[int, List[str]] = {}

    # Split by semicolon for multiple DB entries
    entries = mqs_config.strip().split(";")

    for entry in entries:
        if not entry:
            continue
        try:
            db_part, queue_part = entry.strip().split(":", 1)
            db_num = int(db_part)

            # Split queue names and filter out any empty strings from "q1,,q2"
            queues = [q.strip() for q in queue_part.split(",") if q.strip()]

            if not queues:
                continue

            if db_num in queue_dict:
                queue_dict[db_num].extend(queues)
            else:
                queue_dict[db_num] = queues

        except (ValueError, IndexError):
            # Catches errors from int() conversion or split() if format is wrong.
            # We'll ignore malformed parts.
            continue

    # Ensure all queue lists have unique, sorted names
    for db_num in queue_dict:
        queue_dict[db_num] = sorted(list(set(queue_dict[db_num])))

    return queue_dict
