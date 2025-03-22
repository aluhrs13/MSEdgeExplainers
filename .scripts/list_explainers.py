import re
from pathlib import Path

def get_metadata(file_path):
    """
    Extract metadata from an explainer markdown file.
    
    Returns a dictionary containing:
    - 'heading': The first heading in the file
    - 'issue_tracker': Link to the issue tracker if found
    """
    metadata = {
        'heading': None,
        'issue_tracker': None
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Extract the first heading
            heading_match = re.search(r'# (.+)', content)
            if heading_match:
                metadata['heading'] = heading_match.group(1).strip().replace('*', '').replace('_', '').replace('`', '').replace('<b>', '').replace('</b>', '')
            
            # Extract issue tracker link
            issue_tracker_match = re.search(
                r'https://github\.com/MicrosoftEdge/MSEdgeExplainers/labels/[^\)\s]+',
                content
            )
            if issue_tracker_match:
                metadata['issue_tracker'] = issue_tracker_match.group(0).split("/labels/")[-1].strip().replace("%20", " ")

            # Extract status
            status_match = re.search(
                r'This document status *: (.+)',
                content
            )
            if status_match:    
                status = status_match.group(1).strip()
                status = status.lower().replace('*', '').replace('_', '').replace('`', '').replace('<b>', '').replace('</b>', '').strip()
                if status == "":
                    status = "unlisted"
                metadata['status'] = status
            else:
                metadata['status'] = "unlisted"

            venue_match = re.search(
                r'Current venue *: (.+)',
                content
            )
            if not venue_match:
                venue_match = re.search(
                    r'Expected venue *: (.+)',
                    content
                )

            if venue_match:
                metadata['venue'] = venue_match.group(1).strip()

                
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return metadata


def print_row(item):
    title = item.get('heading', '') or ''
    issue_tracker = item.get('issue_tracker', '') or ''
    status = item.get('status', '') or ''
    venue = item.get('venue', '') or ''
    file_path = item.get('path', '')

    print(f"{file_path:<80} | {title[:47]+'...' if title else '':<50} | {issue_tracker:<50} | {status:<50} | {venue[:47]+'...' if venue else '':<50}")


def update_frontmatter(item):
    base_dir = Path(__file__).resolve().parent.parent

    title = item.get('heading', '') or ''
    issue_tracker = item.get('issue_tracker', '') or ''
    status = item.get('status', '') or ''
    venue = item.get('venue', '') or ''
    file_path = base_dir / item.get('path', '')
    
    if status == "unlisted":
        frontmatter = f'---\nshortname: "{title.replace("\"", "").replace("---", "--")}"\nstatus: "{status}"\n---\n\n'
    else:
        frontmatter = f'---\nshortname: "{title.replace("\"", "").replace("---", "--")}"\nissue_tag: "{issue_tracker}"\nstatus: "{status}"\nvenue: "{venue}"\n---\n\n'
    
    try:
        with open(file_path, 'r+', encoding='utf-8') as file:
            content = file.read()
            file.seek(0, 0)
            file.write(frontmatter + content)
    except Exception as e:
        print(f"Error writing frontmatter to {file_path}: {e}")

def main():
    # Start from the parent directory of .scripts
    base_dir = Path(__file__).resolve().parent.parent
    
    # Track total count
    count = 0

    active = []
    archived = []
    withdrawn =[]
    unknown = []
    
    # Print table header
    print(f"{'Path':<80} | {'Title':<50} | {'Issue Tracker':<50} | {'Status':<50} | {'Venue':<50}")
    print("-" * 80 + "-+-" + "-" * 50 + "-+-" + "-" * 50+ "-+-" + "-" * 50 + "-+-" + "-" * 50)

    try:
        for file in base_dir.glob("**/*.md"):
            file_path = file.relative_to(base_dir)
            if str(file_path).startswith(".") or str(file_path).startswith("README.md") or str(file_path).startswith("CODE_OF_CONDUCT.md"):
                continue
            abs_path = base_dir / file_path
            if abs_path.exists() and abs_path.is_file():
                metadata = get_metadata(abs_path)
                metadata['path'] = str(file_path)

                if metadata.get('status', '') == 'active':
                    active.append(metadata)
                elif metadata.get('status', '') == 'archived':
                    archived.append(metadata)
                elif metadata.get('status', '') == 'withdrawn':
                    withdrawn.append(metadata)
                else:
                    unknown.append(metadata)

                print_row(metadata)
                #update_frontmatter(metadata)

                count += 1
            else:
                print(f"File not found: {file_path}")
    
    except Exception as e:
        print(f"Error reading explainer list: {e}")
    
    print(f"Total markdown files processed: {count}")




if __name__ == "__main__":
    main()
