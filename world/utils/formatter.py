def process_mush_text(text, for_web=False):
    if for_web:
        return text.replace('%r', '<br>')
    else:
        return text.replace('%r', '|\n')