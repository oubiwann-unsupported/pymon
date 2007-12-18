"""
pymon storage module for the Storm ORM
"""

createServiceTable = """

    """

createStatusTable = """
    CREATE TABLE status (
        id INTEGER PRIMARY KEY,
        host VARCHAR,
        service VARCHAR,
        ok_count INTEGER)
    """

createCountsTable = """

    """

createLastTimesTable = """

    """

createEventTable = """
    CREATE TABLE event (
        id INTEGER PRIMARY KEY,
        host VARCHAR,
        service VARCHAR,
        datetime DATETIME,
        transition VARCHAR)
    """
