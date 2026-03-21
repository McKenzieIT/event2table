#!/usr/bin/env python3
"""
Fix FormTable.integration.test.tsx by replacing incorrect patterns
"""

import re

def fix_tests():
    file_path = '/Users/linjiacong/Documents/event2table/frontend/src/shared/ui/components/__tests__/FormTable.integration.test.tsx'
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix 1: Replace filter state with form.watch pattern
    pattern1 = r'const \[filter, setFilter\] = useState\(\'\'\);\s*const form = useForm\(\{ defaultValues: \{ search: \'\' \} \}\);\s*const filteredUsers = initialUsers\.filter\(\s*\(u\) => u\.name\.toLowerCase\(\)\.includes\(filter\.toLowerCase\(\)\) \|\|\s*u\.email\.toLowerCase\(\)\.includes\(filter\.toLowerCase\(\)\)\s*\);'
    replacement1 = '''const form = useForm({ defaultValues: { search: '' } });
        const searchValue = form.watch('search');

        const filteredUsers = initialUsers.filter(
          (u) => u.name.toLowerCase().includes(searchValue.toLowerCase()) ||
                   u.email.toLowerCase().includes(searchValue.toLowerCase())
        );'''
    
    content = re.sub(pattern1, replacement1, content)
    
    # Fix 2: Remove onChange from FormInput
    content = re.sub(r',\s*onChange=\{.*?\}', '', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✓ Fixed FormTable.integration.test.tsx")

if __name__ == '__main__':
    fix_tests()
