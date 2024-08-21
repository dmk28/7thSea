import json
from chargen import PACKAGES

# Dictionary for renaming skills and knacks
RENAME_MAP = {
    "Singing": "Singer",
    "Musician": "Music",
    # Add more mappings as needed
}

def rename_item(name):
    return RENAME_MAP.get(name, name)

def reorganize_packages(packages):
    new_packages = {"Martial": {}, "Civilian": {}, "Professional": {}, "Artist": {}}
    common_knacks = {}

    for category, skills in packages.items():
        for skill, details in skills.items():
            new_category = category
            if category not in new_packages:
                new_category = "Professional"  # Default category

            renamed_skill = rename_item(skill)
            if renamed_skill not in new_packages[new_category]:
                new_packages[new_category][renamed_skill] = {
                    "cost": details.get("cost", 0),
                    "knacks": {},
                    "advanced": {}
                }

            for knack, value in details.get("knacks", {}).items():
                renamed_knack = rename_item(knack)
                new_packages[new_category][renamed_skill]["knacks"][renamed_knack] = value
                if renamed_knack not in common_knacks:
                    common_knacks[renamed_knack] = []
                common_knacks[renamed_knack].append(renamed_skill)

            for adv_knack, adv_value in details.get("advanced", {}).items():
                renamed_adv_knack = rename_item(adv_knack)
                new_packages[new_category][renamed_skill]["advanced"][renamed_adv_knack] = adv_value

    common_knacks = {k: v for k, v in common_knacks.items() if len(v) > 1}
    return new_packages, common_knacks

def write_organized_packages(packages, common_knacks, filename):
    with open(filename, 'w') as f:
        f.write("PACKAGES = {\n")
        for category, skills in packages.items():
            f.write(f"    \"{category}\": {{\n")
            for skill, details in skills.items():
                f.write(f"        \"{skill}\": {{\n")
                f.write(f"            \"cost\": {details['cost']},\n")
                f.write(f"            \"knacks\": {{\n")
                for knack, value in details['knacks'].items():
                    f.write(f"                \"{knack}\": {value},\n")
                f.write(f"            }},\n")
                f.write(f"            \"advanced\": {{\n")
                for adv_knack, adv_value in details['advanced'].items():
                    f.write(f"                \"{adv_knack}\": {adv_value},\n")
                f.write(f"            }}\n")
                f.write(f"        }},\n")
            f.write(f"    }},\n")
        f.write("}\n\n")

        f.write("COMMON_KNACKS = {\n")
        for knack, skills in common_knacks.items():
            f.write(f"    \"{knack}\": {json.dumps(skills)},\n")
        f.write("}\n")

# Run the reorganization
new_packages, common_knacks = reorganize_packages(PACKAGES)

# Write the reorganized structure to a file
output_filename = "chargen2.py"
write_organized_packages(new_packages, common_knacks, output_filename)

print(f"Reorganized packages and common knacks have been written to {output_filename}")