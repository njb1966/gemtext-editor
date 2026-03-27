"""
Parse Gemtext (.gmi) content into a list of typed line objects.

Gemtext is a line-oriented format; each line's type is determined by its prefix.
Preformatted blocks are the only multi-line construct (``` toggle).
"""


def parse_gemtext(content: str) -> list[dict]:
    """
    Parse gemtext content into a list of line objects.

    Returns:
        List of dicts with at minimum a 'type' key and a 'content' key.
        Link lines additionally have 'url' and 'label' keys.
        Preformatted-toggle lines have an 'open' bool key.

    Types: 'link', 'heading1', 'heading2', 'heading3',
           'list', 'quote', 'preformatted', 'preformatted_toggle', 'text'
    """
    result = []
    in_preformatted = False

    for line in content.splitlines():
        if line.startswith("```"):
            in_preformatted = not in_preformatted
            alt_text = line[3:].strip()
            result.append({
                "type": "preformatted_toggle",
                "content": alt_text,
                "open": in_preformatted,
            })
            continue

        if in_preformatted:
            result.append({"type": "preformatted", "content": line})
            continue

        if line.startswith("=>"):
            rest = line[2:].strip()
            parts = rest.split(None, 1)
            url = parts[0] if parts else ""
            label = parts[1] if len(parts) > 1 else url
            result.append({"type": "link", "url": url, "label": label, "content": line})

        elif line.startswith("###"):
            result.append({"type": "heading3", "content": line[3:].strip()})

        elif line.startswith("##"):
            result.append({"type": "heading2", "content": line[2:].strip()})

        elif line.startswith("#"):
            result.append({"type": "heading1", "content": line[1:].strip()})

        elif line.startswith("* "):
            result.append({"type": "list", "content": line[2:]})

        elif line.startswith(">"):
            result.append({"type": "quote", "content": line[1:].strip()})

        else:
            result.append({"type": "text", "content": line})

    return result
