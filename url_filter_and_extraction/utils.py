# Function to extract content excluding the URL
def extract_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        url = lines[0].strip()
        content = "".join(lines[2:]).strip()
    return url, content