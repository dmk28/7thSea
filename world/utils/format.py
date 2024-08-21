import re

def process_ansi_codes(text):
    # Replace %xr with newline and %xt with tab
    text = re.sub(r'%xr', '\n', text)
    text = re.sub(r'%xt', '\t', text)
    return text


def convert_mush_tokens(text):
    """Convert MUSH-style tokens to Evennia-compatible formatting."""
    conversions = {
        '%r': '\n',  # Carriage return
        '%t': '    ',  # Tab (4 spaces)
        '%b': ' ',  # Space
        '%cr': '|r',  # Red color
        '%cg': '|g',  # Green color
        '%cy': '|y',  # Yellow color
        '%cb': '|b',  # Blue color
        '%cm': '|m',  # Magenta color
        '%cc': '|c',  # Cyan color
        '%cw': '|w',  # White color
        '%cn': '|n',  # Reset color
        '%ch': '|h',  # Highlight
        '%cx': '|x',  # Black color
    }
    
    for token, replacement in conversions.items():
        text = text.replace(token, replacement)
    
    return text