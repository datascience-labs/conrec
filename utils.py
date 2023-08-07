def truncate_text(text, max_length=500):
    if len(text) > max_length:
        truncated_text = text[:max_length-3] + "..."
    else:
        truncated_text = text
    return truncated_text