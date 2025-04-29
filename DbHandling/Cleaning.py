
RemoveDuplicates = '''
    DELETE FROM %s
    WHERE record_id NOT IN (
        SELECT MIN(record_id)
        FROM %s
        GROUP BY record_id
    );
'''

