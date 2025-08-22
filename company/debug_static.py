import os
import sys
import django
from django.conf import settings
from django.contrib.staticfiles import finders

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company.settings')
django.setup()

print("=== DJANGO ADMIN STATIC FILES DEBUG ===")
print(f"Django version: {django.VERSION}")
print(f"DEBUG mode: {settings.DEBUG}")
print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")

# Check admin static path
from django.contrib.admin import __path__ as admin_path
admin_static_path = os.path.join(admin_path[0], 'static', 'admin')
print(f"Admin static path: {admin_static_path}")
print(f"Admin static exists: {os.path.exists(admin_static_path)}")

if os.path.exists(admin_static_path):
    print("Admin static contents:")
    for item in os.listdir(admin_static_path):
        item_path = os.path.join(admin_static_path, item)
        print(f"  {item} (dir: {os.path.isdir(item_path)})")

# Test static file finders
print("\n=== TESTING STATIC FILE FINDERS ===")
finders_list = list(finders.get_finders())
print(f"Number of finders: {len(finders_list)}")

for i, finder in enumerate(finders_list):
    print(f"\nFinder {i+1}: {finder}")
    try:
        # Try to find admin files
        found_files = list(finder.list('admin'))
        print(f"  Found {len(found_files)} admin files")
        for path, storage in found_files[:3]:  # Show first 3
            print(f"    {path}")
    except Exception as e:
        print(f"  Error: {e}")

# Test specific admin file
print("\n=== FINDING SPECIFIC ADMIN FILES ===")
test_files = ['admin/js/core.js', 'admin/css/base.css']
for test_file in test_files:
    try:
        result = finders.find(test_file, all=True)
        print(f"{test_file}: {result}")
    except Exception as e:
        print(f"{test_file}: ERROR - {e}")