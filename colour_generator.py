import json
import string
import os

src = os.path.dirname(os.path.realpath(__file__))
json_file = rf"{src}/json/sorted_chars.json"

if not os.path.exists(os.path.dirname(json_file)):
    os.makedirs(os.path.dirname(json_file))

dictionary_of_colours = {}

# Generate a list of printable characters
all_printable_chars = [
    char
    for char in string.printable
    if char in string.ascii_letters
    or char in string.digits
    or char in string.punctuation
    or char in string.whitespace
]

for char in all_printable_chars:
    try:
        hex_code = char.encode("utf-8", errors="surrogateescape").hex()
        dictionary_of_colours[char] = hex_code
    except UnicodeEncodeError:
        pass  # Skip characters that can't be encoded

sorted_chars = sorted(all_printable_chars)
sorted_colours = sorted(dictionary_of_colours.items(), key=lambda x: x[1])
sorted_data = {char: colour for char, colour in sorted_colours}

# Use surrogate escape encoding for writing the JSON file
with open(json_file, "w", encoding="utf-8", errors="surrogateescape") as f:
    json.dump(sorted_data, f, indent=4, ensure_ascii=False)

print(f"Sorted data has been written to {json_file}")
