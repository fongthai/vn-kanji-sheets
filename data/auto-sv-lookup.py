import json
import os
import sys
import time # <-- New: Import the time module

# --- Configuration ---
KANJI_INPUT_FILE = "kanji-org.json"
YOMICHAN_DICTIONARY_FILE = "kanji_bank_1.json"
OUTPUT_FILE = "kanji-with-sv-meanings-final.json"
# ---------------------

def load_dictionary():
    """Loads and preprocesses the Hán-Việt dictionary from the local Yomichan JSON file."""
    # NOTE: This part runs only once and does NOT require a pause as it's a single, local file read.
    print(f"Loading dictionary from: {YOMICHAN_DICTIONARY_FILE}")
    dictionary = {}
    try:
        with open(YOMICHAN_DICTIONARY_FILE, 'r', encoding='utf-8') as f:
            # Yomichan files contain a single list of entries, where each entry is a list of data points.
            yomichan_data = json.load(f)
        
        # Preprocess the data into a simpler {character: [readings]} mapping
        for entry in yomichan_data:
            if len(entry) < 2:
                continue # Skip malformed entries
            
            # The character is always the first item in the list
            character = entry[0] 
            
            # The dictionary definition (meaning) is the second item.
            # This is a list of definition objects.
            definitions = entry[1]

            readings = []
            
            # Look for the Hán-Việt reading inside the definition structure
            for definition in definitions:
                if isinstance(definition, list) and len(definition) > 0:
                    # The Hán-Việt reading is usually the first definition text
                    raw_reading = definition[0]
                    
                    # Clean up the reading string
                    if raw_reading:
                        readings.append(raw_reading.strip())
            
            # Use a set to store unique readings for the character
            unique_readings = set(readings)
            if unique_readings:
                dictionary[character] = list(unique_readings)

        print(f"Dictionary loaded and mapped successfully with {len(dictionary):,} kanji entries.")
        return dictionary
        
    except FileNotFoundError:
        print(f"\n❌ FATAL ERROR: Dictionary file '{YOMICHAN_DICTIONARY_FILE}' not found.")
        print("Please ensure you have downloaded 'kanji_bank_1.json' and placed it in the correct folder.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: An error occurred while reading the dictionary file: {e}")
        sys.exit(1)

def get_han_viet_reading(character, dictionary):
    """Retrieves the Hán-Việt reading for a character from the loaded dictionary."""
    # The dictionary value is a list of readings, e.g., ["PHÂN"]
    readings = dictionary.get(character)
    
    if readings:
        # Format as CAPITALIZED, comma-separated string
        return ", ".join(r.upper() for r in sorted(readings))
    
    return None

def process_kanji_file():
    """Reads the kanji data, looks up Hán-Việt offline, and writes the output."""
    
    hvd_dictionary = load_dictionary()
    
    print(f"Reading input file: {KANJI_INPUT_FILE}")
    sys.stdout.flush()
    
    # 1. Read the input file
    try:
        with open(KANJI_INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        print(f"❌ FATAL ERROR: Could not read or decode JSON from '{KANJI_INPUT_FILE}'.")
        return

    kanji_list = data.get('kanji', [])
    total_kanji = len(kanji_list)
    modified_count = 0
    skipped_count = 0
    
    # ⚠️ IMPORTANT: Since the dictionary is loaded into memory (offline), 
    # the lookups below are instantaneous and do not trigger rate limits.
    # The pause is added purely to meet your request, but it is not necessary 
    # to prevent rate limiting.
    print(f"Found {total_kanji} kanji entries. Starting lookup with 5-second delay per entry...")
    sys.stdout.flush()
    
    # 2. Iterate and modify the 'meaning' field
    for i, kanji_entry in enumerate(kanji_list):
        character = kanji_entry.get('character')
        current_meaning = kanji_entry.get('meaning')
        
        if character and current_meaning is not None:
            
            # Print status update
            print(f"Processing {i+1}/{total_kanji}: '{character}'...", end='\r')
            sys.stdout.flush()

            sv_meaning = get_han_viet_reading(character, hvd_dictionary)
            
            # Clear the current line after processing
            print(" ".ljust(80), end='\r') 

            if sv_meaning:
                # Update status with successful reading
                print(f"✅ Processed {i+1}/{total_kanji}: '{character}' -> {sv_meaning.ljust(30)}")
                
                # Requested format: "HÁN VIỆT READINGS, existing meaning"
                if current_meaning.strip():
                     new_meaning = f"{sv_meaning}, {current_meaning}"
                else:
                    new_meaning = sv_meaning
                
                kanji_entry['meaning'] = new_meaning
                modified_count += 1
            else:
                skipped_count += 1
        
        # ADD THE PAUSE HERE (5 seconds per kanji)
        time.sleep(5) 

    # 3. Write the output file
    try:
        data['kanji'] = kanji_list 
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"\n" + "="*50)
        print(f"✅ Processing Complete and File Saved!")
        print(f"   Output saved to: {OUTPUT_FILE}")
        print(f"   {modified_count} kanji entries were updated with Hán-Việt readings.")
        print(f"   {skipped_count} kanji entries were skipped (Hán-Việt reading not found in dictionary).")
        print("="*50)
    except Exception as e:
        print(f"❌ FATAL ERROR: Could not write output file {OUTPUT_FILE}: {e}")
        
if __name__ == "__main__":
    process_kanji_file()