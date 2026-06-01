def extract_text(content) -> str:
    if not isinstance(content, list):
        return str(content)
    return "\n".join([block.text for block in content if block.type == "text"])