import re

with open('README.md', 'r') as f:
    content = f.read()

# Fix <== "text" ==>
content = re.sub(r'<==\s+"([^"]+)"\s+==>', r'<==>|"\1"|', content)
# Fix -- "text" -->
content = re.sub(r'--\s+"([^"]+)"\s+-->', r'-->|"\1"|', content)

with open('README.md', 'w') as f:
    f.write(content)

