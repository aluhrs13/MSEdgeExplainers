import re
from pathlib import Path
import yaml  # Add this import

base_dir = Path(__file__).resolve().parent.parent


# TODO: Make issue templates! (.github\ISSUE_TEMPLATE\)
# https://github.com/MicrosoftEdge/MSEdgeExplainers/issues/new?template=acquisition-info.md

def get_metadata(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read YAML frontmatter if present
            content = file.read()
            if content.startswith('---'):
                frontmatter_end = content.find('---', 3) + 3
                frontmatter = content[3:frontmatter_end-3]  # Extract YAML content between '---'
                content = content[frontmatter_end:].lstrip()
                try:
                    metadata = yaml.safe_load(frontmatter)
                    metadata['file_path'] = str(Path(file_path).relative_to(base_dir))
                    return metadata
                    
                except yaml.YAMLError as e:
                    print(f"Error parsing YAML in {file_path}: {e}")
                    return {}
            else:
                print(f"Warning: No YAML frontmatter found in {file_path}.")
                return {}
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}

def print_row(item, type):
    shortname = item.get('shortname', '')
    issue_tracker = item.get('issue_tag', '')
    status = item.get('status', '')
    venue = item.get('venue', '')

    print(f"{shortname:<120} | {issue_tracker:<40} | {status:<20} | {venue:<50}")


def print_markdown_row(item, type):
    shortname = item.get('shortname', '')
    issue_tracker = item.get('issue_tag', '')
    status = item.get('status', '')
    venue = item.get('venue', '')
    file_path = item.get('file_path', '').replace("\\", "/").replace(" ", "%20")

    row_str = f"| [{shortname}]({file_path})"

    if type == "active":
        if issue_tracker:
            row_str += f"| <a href=\"https://github.com/MicrosoftEdge/MSEdgeExplainers/labels/{issue_tracker.replace(" ", "%20")}\">![GitHub issues by-label](https://img.shields.io/github/issues/MicrosoftEdge/MSEdgeExplainers/{issue_tracker.replace(" ", "%20")}?label=issues)</a>"
        else:
            row_str += f"| "
        row_str += f"| [New issue...](https://github.com/MicrosoftEdge/MSEdgeExplainers/issues/new?template={issue_tracker.replace(" ", "-").lower()}.md)"
        row_str += f"| {venue} |"
    elif type == "withdrawn":
        row_str += f"| {item.get('withdrawn_reason', '')}"
        row_str += f"| {item.get('last_change', '')}"

    return row_str


def create_issue_template(item):
    issue_template = f"""---
name: {item.get('shortname', '')}
about: Issues for {item.get('shortname', '')}
title: "[{item.get('shortname', '')}] <TITLE HERE>"
labels: {item.get('issue_tag', '').replace("%20", " ")}

---
"""
    file_name = item.get('issue_tag', '').replace(" ", "-").lower() + ".md"
    file_path = base_dir /  ".github/ISSUE_TEMPLATE/" / file_name
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(issue_template)

    return issue_template

def write_markdown_tables(active, withdrawn, archived, unlisted):
    with open("../TEST_README.md", "w", encoding="utf-8") as f:
        f.write("# Explainers\n")
        f.write("## Active Explainers\n")
        f.write("| Explainer | Issues | Feedback | Expected Venue |\n")
        f.write("| --- | --- | --- | --- |\n")
        for item in active:
            create_issue_template(item)
            print_row(item, "active")
            f.write(print_markdown_row(item, "active") + "\n")

        f.write("\n## Withdrawn Explainers\n")
        f.write("| Shortname | Issue Tracker | Venue |\n")
        f.write("| --- | --- | --- |\n")
        for item in withdrawn:
            f.write(print_markdown_row(item, "withdrawn") + "\n")

        f.write("\n## Archived Explainers\n")
        f.write("| Shortname | Issue Tracker | Venue |\n")
        f.write("| --- | --- | --- |\n")
        #for item in archived:
        #    print_row(item, "archived")

        f.write("\n## Unlisted Explainers\n")
        f.write("| Shortname | Issue Tracker | Venue |\n")
        f.write("| --- | --- | --- |\n")
        #for item in unlisted:
        #    print_row(item, "unlisted")

def main():
    count = 0

    active = []
    withdrawn = []
    archived = []
    unlisted = []

    try:
        for file in base_dir.glob("**/*.md"):
            file_path = file.relative_to(base_dir)
            if str(file_path).startswith(".") or str(file_path).startswith("README.md") or str(file_path).startswith("CODE_OF_CONDUCT.md"):
                continue
            abs_path = base_dir / file_path
            if abs_path.exists() and abs_path.is_file():
                metadata = get_metadata(abs_path)

                if metadata.get('status') == "active":
                    active.append(metadata)
                elif metadata.get('status') == "withdrawn":
                    withdrawn.append(metadata)
                elif metadata.get('status') == "archived":
                    archived.append(metadata)
                elif metadata.get('status') == "unlisted":
                    unlisted.append(metadata)
                else:
                    print(f"Unknown status for {file_path}: {metadata.get('status')}")
                count += 1
    except Exception as e:
        print(f"Error reading explainer list: {e}")
        return
    
    print(f"\nTotal files processed: {count}")
    print(f"\tActive: {len(active)}")
    print(f"\tWithdrawn: {len(withdrawn)}")
    print(f"\tArchived: {len(archived)}")
    print(f"\tUnlisted: {len(unlisted)}")
    
    write_markdown_tables(active, withdrawn, archived, unlisted)


if __name__ == "__main__":
    main()
