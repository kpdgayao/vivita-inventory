import os
import sys

print("Current working directory:", os.getcwd())
print("\nPython path:")
for path in sys.path:
    print(path)

print("\nChecking if app/main.py exists:")
print(os.path.exists("app/main.py"))
print(os.path.exists(os.path.join(os.getcwd(), "app", "main.py")))

print("\nListing directory contents:")
print(os.listdir("."))
