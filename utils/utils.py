

def clean_file_path(prompt: str):
    return prompt.replace('/', '').replace('?', '').replace('"', '').replace('*', '').replace('|', '').replace('\\', '').replace(':', '').replace(';', '').replace('>', '').replace('<', '')
