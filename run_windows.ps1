# Set PYTHONPATH to the current directory
$env:PYTHONPATH = (Get-Location)

# Run the chainlit command
chainlit run app/chat.py -w