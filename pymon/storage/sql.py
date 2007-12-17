"""
pymon storage module for the Storm ORM
"""

createStatusTable = """
    CREATE TABLE status (
        id INTEGER PRIMARY KEY,
        host VARCHAR,
        service VARCHAR,
        ok_count INTEGER)
    """

createEventTable = """
    CREATE TABLE event (
        id INTEGER PRIMARY KEY,
        host VARCHAR,
        service VARCHAR,
        datetime DATETIME,
        transition VARCHAR)
    """
