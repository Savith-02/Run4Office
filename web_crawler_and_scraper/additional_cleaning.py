import re

def clean_html(text):
    text = replace_repeating_opening_tags(text)
    text = replace_repeating_closing_tags(text)
    return strip_structure(text)

# Function to replace repeating opening tags with a single tag
def replace_repeating_opening_tags(text):
    # This will match consecutive opening tags of the same type and replace with a single tag
    return re.sub(r'(<(\w+)>)(\s*<\2>)+', r'\1', text)

# Function to replace repeating closing tags with a single tag
def replace_repeating_closing_tags(text):
    # This will match consecutive closing tags of the same type and replace with a single closing tag
    return re.sub(r'(</(\w+)>)(\s*</\2>)+', r'\1', text)

def strip_structure(text):
    # Split the text into lines, strip each line, and filter out empty lines
    cleaned_text = '\n'.join([line.strip() for line in text.splitlines() if line.strip()])
    return cleaned_text

