def Escape(text, restricted):
    for char in restricted:
        text = text.replace(char, f"\\{char}")
    return text


def EscapeMarkdownLink(text):
    return Escape(text, [')', '\\'])


def EscapeMarkdownCode(text):
    return Escape(text, ['`', '\\'])


def EscapeMarkdown(text):
    return Escape(text, [
        '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|',
        '{', '}', '.', '!'
    ])
