import json
import os

def split_kanji_by_jlpt_level(input_filename="kanji-org.json"):
    """
    Reads the input JSON file, filters kanji by 'category', and writes 
    the results to five separate JLPT level files.
    """
    
    print(f"Reading input file: {input_filename}")
    
    # 1. Read the input file
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found. Please make sure it's in the same directory.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{input_filename}'. Please check its formatting.")
        return

    # Assuming the structure is {"kanji": [...]}
    kanji_list = data.get('kanji', [])

    if not kanji_list:
        print("Warning: 'kanji' array is empty or missing in the input file.")
        return

    # 2. Group kanji by category
    jlpt_groups = {
        'jlptn5': [],
        'jlptn4': [],
        'jlptn3': [],
        'jlptn2': [],
        'jlptn1': []
    }

    for kanji in kanji_list:
        category = kanji.get('category', '').lower()
        if category in jlpt_groups:
            jlpt_groups[category].append(kanji)

    # 3. Write output files
    output_filenames = {
        'jlptn5': "kanji-jlpt-n5.json",
        'jlptn4': "kanji-jlpt-n4.json",
        'jlptn3': "kanji-jlpt-n3.json",
        'jlptn2': "kanji-jlpt-n2.json",
        'jlptn1': "kanji-jlpt-n1.json"
    }

    print("\nStarting file creation...")
    for category_key, output_filename in output_filenames.items():
        output_data = {
            "kanji": jlpt_groups[category_key]
        }
        
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=4)
            print(f"✅ Created {output_filename} with {len(jlpt_groups[category_key])} entries.")
        except Exception as e:
            print(f"❌ Error writing file {output_filename}: {e}")
            
    print("\nProcess complete.")

if __name__ == "__main__":
    split_kanji_by_jlpt_level()