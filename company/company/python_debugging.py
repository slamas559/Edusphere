# Debug script to check AppDirectoriesFinder
import os
import django
from django.conf import settings
from django.contrib.staticfiles.finders import AppDirectoriesFinder

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company.settings')
django.setup()

finder = AppDirectoriesFinder()
print("=== APP DIRECTORIES FINDER ===")
print(f"Storage: {finder.storage}")
print(f"Apps: {finder.apps}")

# Check if it can find admin files
try:
    result = list(finder.list('admin'))
    print(f"Found admin files: {len(result)}")
    for path, storage in result[:5]:  # Show first 5
        print(f"  {path}")
except Exception as e:
    print(f"Error: {e}")