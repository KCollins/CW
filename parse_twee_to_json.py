import re
import json
import sys

def parse_twee_to_game_json(twee_filepath, title="Custom Adventure", author="Unknown"):
    with open(twee_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split Twee file by passage headers (:: PassageName)
    raw_passages = re.split(r'\n::\s*', content)
    rooms = {}
    start_room = None

    for passage in raw_passages:
        if not passage.strip():
            continue
        lines = passage.strip().split('\n')
        header = lines[0].strip()
        
        # Extract passage name (e.g., "West of House [tags]")
        passage_name = header.split('[')[0].strip()
        room_id = passage_name.lower().replace(' ', '_')

        if not start_room and not passage_name.startswith('Story'):
            start_room = room_id

        body = '\n'.join(lines[1:])
        exits = {}
        
        # Extract Twine links [[Link Text->Target]] or [[Target]]
        link_pattern = r'\[\[(?:([^\]\|]+)->)?([^\]\|]+)\]\]'
        for match in re.finditer(link_pattern, body):
            label = match.group(1) or match.group(2)
            target = match.group(2).strip().lower().replace(' ', '_')
            
            # Map directional labels
            cmd = label.strip().lower()
            exits[cmd] = target

        # Clean Twine markup out of description
        clean_desc = re.sub(r'\[\[.*?\]\]', '', body).strip()

        rooms[room_id] = {
            "name": passage_name.upper(),
            "desc": clean_desc,
            "exits": exits,
            "items": []
        }

    game_data = {
        "title": title,
        "author": author,
        "startRoom": start_room or list(rooms.keys())[0],
        "rooms": rooms
    }

    return game_data

if __name__ == "__main__":
    if len(sys.argv) > 1:
        data = parse_twee_to_game_json(sys.argv[1])
        with open("converted_game.json", "w") as out:
            json.dump(data, out, indent=2)
        print("Successfully created converted_game.json!")
