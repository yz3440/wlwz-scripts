# remove page numbers from script text
def remove_page_numbers(script_text: str) -> str:
    # Read all lines
    lines = script_text.split("\n")

    # Filter out lines that are just small numbers
    filtered_lines = []
    for line in lines:
        line = line.strip()
        try:
            num = int(line)
        except ValueError:
            filtered_lines.append(line)

    return "\n".join(filtered_lines)
