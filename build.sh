# Create the directories and init files
mkdir -p tools prompts agents agent_graph app models config

# Create __init__.py files in each directory
echo "# This file marks the directory as a Python package" > tools/__init__.py
echo "# This file marks the directory as a Python package" > prompts/__init__.py
echo "# This file marks the directory as a Python package" > agents/__init__.py
echo "# This file marks the directory as a Python package" > agent_graph/__init__.py
echo "# This file marks the directory as a Python package" > app/__init__.py
echo "# This file marks the directory as a Python package" > models/__init__.py
echo "# This file marks the directory as a Python package" > config/__init__.py

echo "Folder structure created successfully."
