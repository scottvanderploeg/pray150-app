import re

# Read the original SVG
with open('static/images/pray150-logo-horizontal.svg', 'r') as f:
    content = f.read()

# Extract the style section
style_section = re.search(r'<style>(.*?)</style>', content, re.DOTALL).group(1)

# Find all path elements
path_pattern = r'<path[^>]*class="([^"]*)"[^>]*d="([^"]*)"[^>]*/?>'
paths = re.findall(path_pattern, content)

# Separate paths based on Y coordinates
top_paths = []
bottom_paths = []

for class_name, path_data in paths:
    # Find Y coordinates in the path data
    y_coords = re.findall(r'[ML](\d+),(\d+)', path_data)
    if y_coords:
        avg_y = sum(int(y) for x, y in y_coords) / len(y_coords)
        if avg_y < 500:
            top_paths.append((class_name, path_data))
        else:
            bottom_paths.append((class_name, path_data))

# Create top SVG
top_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg id="Layer_1" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 500">
  <defs>
    <style>{style_section}</style>
  </defs>
  <rect class="cls-33" width="1000" height="500"/>
'''

for class_name, path_data in top_paths:
    top_svg += f'  <path class="{class_name}" d="{path_data}"/>\n'

top_svg += '</svg>'

# Create bottom SVG  
bottom_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg id="Layer_1" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 500 1000 500">
  <defs>
    <style>{style_section}</style>
  </defs>
  <rect class="cls-33" width="1000" height="500"/>
'''

for class_name, path_data in bottom_paths:
    bottom_svg += f'  <path class="{class_name}" d="{path_data}"/>\n'

bottom_svg += '</svg>'

# Write the files
with open('static/images/pray150-logo-top.svg', 'w') as f:
    f.write(top_svg)

with open('static/images/pray150-logo-bottom.svg', 'w') as f:
    f.write(bottom_svg)

print(f'Created top logo with {len(top_paths)} paths')
print(f'Created bottom logo with {len(bottom_paths)} paths')
