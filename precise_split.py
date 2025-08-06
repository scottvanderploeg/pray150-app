import re

with open('static/images/pray150-logo-horizontal.svg', 'r') as f:
    content = f.read()

# Extract the style section
style_section = re.search(r'<style>(.*?)</style>', content, re.DOTALL).group(1)

# Find all path elements with their bounding boxes
path_pattern = r'<path[^>]*class="([^"]*)"[^>]*d="([^"]*)"[^>]*/?>'
paths = re.findall(path_pattern, content)

top_paths = []
bottom_paths = []

for class_name, path_data in paths:
    # Find all coordinates in the path
    coords = re.findall(r'[ML](\d+),(\d+)', path_data)
    
    if coords:
        y_values = [int(y) for x, y in coords]
        min_y = min(y_values)
        max_y = max(y_values)
        
        # Use a more conservative split - elements that are primarily in top half vs bottom half
        if max_y < 400:  # Clearly in top portion
            top_paths.append((class_name, path_data))
        elif min_y > 600:  # Clearly in bottom portion  
            bottom_paths.append((class_name, path_data))
        else:
            # For elements that span both, decide based on where most of the path is
            avg_y = sum(y_values) / len(y_values)
            if avg_y < 500:
                top_paths.append((class_name, path_data))
            else:
                bottom_paths.append((class_name, path_data))

# Create top SVG with adjusted viewBox to show only the top portion
top_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg id="Layer_1" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 400">
  <defs>
    <style>{style_section}</style>
  </defs>
  <rect class="cls-33" width="1000" height="400"/>
'''

for class_name, path_data in top_paths:
    top_svg += f'  <path class="{class_name}" d="{path_data}"/>\n'

top_svg += '</svg>'

# Create bottom SVG with adjusted viewBox to show only the bottom portion
bottom_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg id="Layer_1" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 600 1000 400">
  <defs>
    <style>{style_section}</style>
  </defs>
  <rect class="cls-33" width="1000" height="400"/>
'''

for class_name, path_data in bottom_paths:
    bottom_svg += f'  <path class="{class_name}" d="{path_data}"/>\n'

bottom_svg += '</svg>'

# Write the files
with open('static/images/pray150-logo-top.svg', 'w') as f:
    f.write(top_svg)

with open('static/images/pray150-logo-bottom.svg', 'w') as f:
    f.write(bottom_svg)

print(f'Created precise top logo with {len(top_paths)} paths (Y < 400)')
print(f'Created precise bottom logo with {len(bottom_paths)} paths (Y > 600)')
print(f'Top logo viewBox: 0 0 1000 400')
print(f'Bottom logo viewBox: 0 600 1000 400')
