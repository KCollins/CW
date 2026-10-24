import os
import re
import json
import sys

def parse_story_directory(story_dir, title="Keep of the Mad Wizard", author="Felix Pleșoianu"):
    rooms = {}
    start_room = None

    # Recursively find all Twee/Twine source or HTML files
    matching_files = []
    valid_exts = ('.twee', '.tw', '.twee2', '.txt', '.html', '.htm')
    
    for root, _, files in os.walk(story_dir):
        for file in files:
            if file.lower().endswith(valid_exts):
                matching_files.append(os.path.join(root, file))

    if not matching_files:
        print(f"Warning: No matching story files found in {story_dir}")
        return None

    for filepath in matching_files:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Check if file is a compiled Twine HTML export (<tw-passagedata>)
        if '<tw-passagedata' in content.lower():
            passage_matches = re.findall(r'<tw-passagedata[^>]*name=["\']([^"\']+)["\'][^>]*>(.*?)</tw-passagedata>', content, re.DOTALL | re.IGNORECASE)
            for name, body in passage_matches:
                room_id = name.lower().strip().replace(' ', '_')
                if not start_room and room_id not in ['storytitle', 'storysettings']:
                    start_room = room_id
                
                exits = {}
                link_pattern = r'\[\[(?:([^\]\|]+)(?:->|\|))?([^\]\|]+)\]\]'
                for match in re.finditer(link_pattern, body):
                    label = match.group(1) or match.group(2)
                    target = match.group(2).strip().lower().replace(' ', '_')
                    exits[label.strip().lower()] = target

                clean_desc = re.sub(r'<[^>]+>', '', body)
                clean_desc = re.sub(r'\[\[.*?\]\]', '', clean_desc)
                clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()

                rooms[room_id] = {
                    "name": name.upper(),
                    "desc": clean_desc,
                    "exits": exits,
                    "items": []
                }
        else:
            # Standard Twee format (:: PassageName)
            raw_passages = re.split(r'\n::\s*', '\n' + content)
            for passage in raw_passages:
                if not passage.strip():
                    continue
                
                lines = passage.strip().split('\n')
                header = lines[0].strip()
                passage_name = header.split('[')[0].strip()
                room_id = passage_name.lower().replace(' ', '_')

                if passage_name.lower() in ['start', 'storytitle', 'main'] and not start_room:
                    start_room = room_id

                body = '\n'.join(lines[1:])
                exits = {}

                link_pattern = r'\[\[(?:([^\]\|]+)(?:->|\|))?([^\]\|]+)\]\]'
                for match in re.finditer(link_pattern, body):
                    label = match.group(1) or match.group(2)
                    target = match.group(2).strip().lower().replace(' ', '_')
                    exits[label.strip().lower()] = target

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

    if not rooms:
        return None

    first_room = list(rooms.keys())[0]

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

    story_data = parse_story_directory(input_dir)
    if story_data:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(story_data, f, indent=2)
        print(f"Successfully converted {input_dir} -> {output_file}")
    else:
        print(f"Error: Could not convert story in {input_dir}")
        sys.exit(1)
