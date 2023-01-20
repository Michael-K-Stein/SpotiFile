ILLEGAL_FILE_NAME_CHARACTERS = '/?"*|\\:;><#%{}$!\'@`='


def clean_file_path(prompt: str):
    for illegal_char in ILLEGAL_FILE_NAME_CHARACTERS:
        prompt = prompt.replace(illegal_char, '')
    return prompt
