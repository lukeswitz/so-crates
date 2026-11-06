#!/usr/bin/env python3
"""Event extraction helpers for Suricata eve.json data."""


def get_timestamp(event):
    return event.get('timestamp', '')


def _nested(event, key, field, default):
    """An ECS-style {key: {field: ...}} value - only when key holds an
    object: tshark's rows carry source: 'tshark', a string."""
    value = event.get(key)
    return value.get(field, default) if isinstance(value, dict) else default


def get_src_ip(event):
    return event['src_ip'] if 'src_ip' in event else _nested(event, 'source', 'ip', '')


def get_src_port(event):
    return event['src_port'] if 'src_port' in event else _nested(event, 'source', 'port', 0)


def get_dest_ip(event):
    return event['dest_ip'] if 'dest_ip' in event else _nested(event, 'destination', 'ip', '')


def get_dest_port(event):
    return event['dest_port'] if 'dest_port' in event else _nested(event, 'destination', 'port', 0)


def get_protocol(event):
    return event.get('proto', '')


def get_app_proto(event):
    return event.get('app_proto', '')
