import json
import re

def clean_text(text):
    """Remove all bracketed tags from text"""
    # Remove anything in square brackets
    cleaned = re.sub(r'\[.*?\]', '', text)
    # Clean up extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def is_low_value(text):
    """Check if a chunk should be filtered out"""
    text_lower = text.lower().strip()

    # Empty or too short
    if len(text_lower) < 10:
        return True

    # Common greetings/banter patterns
    greeting_patterns = [
        r"^(hey|hi|hello|yo|what's up|sup|howdy)[\s\W]*$",
        r"^thanks for watching",
        r"^don't forget to subscribe",
        r"^like and subscribe",
        r"^thanks for listening",
        r"^hit that like button",
    ]

    for pattern in greeting_patterns:
        if re.match(pattern, text_lower):
            return True

    # Check if text is mostly banter/off-topic (no relevant keywords)
    athletic_keywords = {
        'jump', 'vertical', 'leap', 'athletic', 'training', 'exercise',
        'fitness', 'strength', 'power', 'muscle', 'workout', 'sport',
        'performance', 'conditioning', 'plyometric', 'explosive', 'height',
        'technique', 'form', 'stride', 'velocity', 'acceleration',
        'coach', 'athlete', 'physical', 'endurance', 'sprint', 'bound',
        'lift', 'squat', 'press', 'run', 'drill', 'program', 'set', 'rep',
        'intensity', 'recovery', 'nutrition', 'core', 'legs', 'glutes',
        'hamstring', 'quadriceps', 'calf', 'ankle', 'knee', 'hip',
        'biomechanics', 'mechanics', 'movement'
    }

    # Count keyword occurrences
    keywords_found = sum(1 for keyword in athletic_keywords if keyword in text_lower)

    # If text is longer but has no athletic keywords, likely not relevant
    if len(text_lower) > 50 and keywords_found == 0:
        return True

    return False

def clean_rag_dataset(input_file, output_file):
    """Filter and clean the RAG dataset"""
    removed_count = 0
    kept_count = 0

    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:

        for line_num, line in enumerate(infile, 1):
            try:
                record = json.loads(line)

                # Extract text content (handle various possible field names)
                text = record.get('text') or record.get('content') or record.get('chunk') or str(record)

                if not is_low_value(text):
                    # Clean bracketed tags from the text
                    cleaned_text = clean_text(text)

                    # Update the record with cleaned text
                    if 'text' in record:
                        record['text'] = cleaned_text
                    elif 'content' in record:
                        record['content'] = cleaned_text
                    elif 'chunk' in record:
                        record['chunk'] = cleaned_text

                    # Write the updated record
                    outfile.write(json.dumps(record, ensure_ascii=False) + '\n')
                    kept_count += 1
                else:
                    removed_count += 1

                if line_num % 100 == 0:
                    print(f"Processed {line_num} lines... (Kept: {kept_count}, Removed: {removed_count})")

            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}")
                continue

    print(f"\nCleaning complete!")
    print(f"Total kept: {kept_count}")
    print(f"Total removed: {removed_count}")
    print(f"Output saved to: {output_file}")

if __name__ == "__main__":
    input_path = r"C:\Users\chaze\OneDrive\Desktop\APPS\thp-rag\rag_dataset.jsonl"
    output_path = r"C:\Users\chaze\OneDrive\Desktop\APPS\thp-rag\cleaned_rag_dataset.jsonl"

    clean_rag_dataset(input_path, output_path)
