import re
from pathlib import Path

# Fix all detector files
detector_dirs = [
    'detectors/performance',
    'detectors/frontend', 
    'detectors/graphql',
    'detectors/architecture'
]

for detector_dir in detector_dirs:
    dir_path = Path(detector_dir)
    if not dir_path.exists():
        print(f"⚠️  Skipping {detector_dir} (not found)")
        continue
    
    for py_file in dir_path.glob('*.py'):
        if py_file.name == '__init__.py':
            continue
            
        content = py_file.read_text()
        original_content = content
        
        # Replace relative imports with absolute imports
        content = re.sub(
            r'from \.\.\.core\.base_detector import',
            'from core.base_detector import',
            content
        )
        
        if content != original_content:
            py_file.write_text(content)
            print(f"✅ Fixed: {py_file}")
        else:
            print(f"○ No changes: {py_file}")

print("\n✅ Import fixes completed")
