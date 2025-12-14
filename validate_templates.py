import os
import re

TEMPLATE_DIR = r'g:\UNI\303 web dev\project\templates'

def check_templates():
    errors = []
    
    # Tags that must be closed
    TAG_PAIRS = {
        'if': 'endif',
        'for': 'endfor',
        'block': 'endblock',
        'with': 'endwith',
        'comment': 'endcomment'
    }
    
    # Regex to find tags: {% tag_name ... %}
    # Capture the tag name
    tag_pattern = re.compile(r'{%\s*([a-zA-Z0-9_]+)')
    
    for filename in os.listdir(TEMPLATE_DIR):
        if not filename.endswith('.html'):
            continue
            
        filepath = os.path.join(TEMPLATE_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        stack = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Find all tags in the line
            matches = tag_pattern.finditer(line)
            for match in matches:
                tag_name = match.group(1)
                
                if tag_name in TAG_PAIRS:
                    stack.append((tag_name, i + 1))
                elif tag_name.startswith('end'):
                    # Check if it matches the last open tag
                    expected_end = tag_name
                    
                    found_match = False
                    # Check reversed stack for matching open tag
                    # (Simple stack check suffices for well-nested, but tolerant to intermediate ignores)
                    if stack:
                        last_tag, last_line = stack[-1]
                        if TAG_PAIRS.get(last_tag) == tag_name:
                            stack.pop()
                            found_match = True
                        else:
                            # Mismatch
                            errors.append(f"{filename}:{i+1}: Found {{% {tag_name} %}} but expected {{% {TAG_PAIRS.get(last_tag, 'unknown')} %}} for {{% {last_tag} %}} on line {last_line}")
                    else:
                        errors.append(f"{filename}:{i+1}: Found {{% {tag_name} %}} without opening tag")

        if stack:
            for tag, line in stack:
                errors.append(f"{filename}:{line}: Unclosed {{% {tag} %}} tag")

    if errors:
        print("Found Template Errors:")
        for e in errors:
            print(e)
    else:
        print("No basic template syntax errors found.")

if __name__ == "__main__":
    check_templates()
