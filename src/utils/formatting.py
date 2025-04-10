def format_timestamp(dt):
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")
