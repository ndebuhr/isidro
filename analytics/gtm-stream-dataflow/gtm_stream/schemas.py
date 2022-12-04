raw_stream_bq_schema = {
    'fields': [
        {'name': 'container_id', 'type': 'STRING'},
        {'name': 'container_version', 'type': 'STRING'},
        {'name': 'cookie_enabled', 'type': 'BOOL'},
        {'name': 'debug_mode', 'type': 'BOOL'},
        {'name': 'environment_name', 'type': 'STRING'},
        {'name': 'event', 'type': 'STRING'},
        {'name': 'language', 'type': 'STRING'},
        {'name': 'languages', 'type': 'STRING', 'mode': 'REPEATED'},
        {'name': 'online', 'type': 'BOOL'},
        {'name': 'page_hostname', 'type': 'STRING'},
        {'name': 'page_path', 'type': 'STRING'},
        {'name': 'page_url', 'type': 'STRING'},
        {'name': 'random_number', 'type': 'INT64'},
        {'name': 'referrer', 'type': 'STRING'},
        {'name': 'scroll_x', 'type': 'FLOAT64'},
        {'name': 'scroll_y', 'type': 'FLOAT64'},
        {'name': 'timestamp', 'type': 'TIMESTAMP'},
        {'name': 'user_agent', 'type': 'STRING'}
    ]
}