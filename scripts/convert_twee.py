import os
import re
import json
import sys

def parse_twee_directory(story_dir, title="Keep of the Mad Wizard", author="Felix Pleșoianu"):
    rooms = {}
    start_room = None

    # Recursively find all .twee files in the story folder
    twee_files = []
    for root, _, files in os.walk(story_dir):
        for file in files:
            if file.endswith('.twee') or file.endswith('.tw'):
                twee_files.append(os.path.join(root, file))

    if not twee_files:
        raise FileNotFoundError(f"No .twee files found in directory {story_dir}")

    for filepath in twee_files:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Split passage headers (:: PassageName [tags])
        raw_passages = re.split(r'\n::\s*', '\n' + content)
        
        for passage in raw_passages:
            if not passage.strip():
                continue
            
            lines = passage.strip().split('\n')
            header = lines[0].strip()
            
            # Extract passage name (ignore tags like [nogoto])
            passage_name = header.split('[')[0].strip()
            room_id = passage_name.lower().replace(' ', '_')

            # Identify start room (defaulting to 'Start' or 'StoryTitle' setup)
            if passage_name.lower() in ['start', 'storytitle', 'main'] and not start_room:
                start_room = room_id

            body = '\n'.join(lines[1:])
            exits = {}

            # Extract links: [[Text->Target]], [[Text|Target]], or [[Target]]
            link_pattern = r'\[\[(?:([^\]\|]+)(?:->|\|))?([^\]\|]+)\]\]'
            for match in re.finditer(link_pattern, body):
                label = match.group(1) or match.group(2)
                target = match.group(2).strip().lower().replace(' ', '_')
                
                cmd = label.strip().lower()
                exits[cmd] = target

            # Clean Twine/SugarCube macros (e.g. <<set ...>>, <<if ...>>, <<include ...>>)
            clean_desc = re.sub(r'<<.*?>>', '', body)
            clean_desc = re.sub(r'\[\[.*?\]\]', '', clean_desc)
            clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()

            if clean_desc or exits:
                rooms[room_id] = {
                    "name": passage_name.upper(),
                    "desc": clean_desc,
                    "exits": exits,
                    "items": []
                }

    # Fallback start room if no 'Start' passage header existed
    first_room = list(rooms.keys())[0] if rooms else "start"

    return {
        "title": title,
        "author": author,
        "startRoom": start_room if start_room in rooms else first_room,
        "rooms": rooms
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_twee.py <input_story_dir> <output_json_file>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_file = sys.argv[2]

    story_data = parse_twee_directory(input_dir)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(story_data, f, indent=2)

    print(f"Successfully converted {input_dir} -> {output_file}")
