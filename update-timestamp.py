"""
Timestamp Update Service for Claude Code
Updates .claude-timestamp file every 60 seconds with current local time.
Run this in the background: python update-timestamp.py
"""
import time

print("Timestamp Update Service for Claude Code")
print("Writing to .claude-timestamp every 60 seconds")
print("Press Ctrl+C to stop")
print("-" * 50)

while True:
    lastTime = time.time()

    # Write timestamp to file
    timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S')
    with open('.claude-timestamp', 'w') as f:
        f.write(timestamp_str)

    # Print confirmation
    print(f"Updated .claude-timestamp to {timestamp_str}")

    # Sleep until exactly 60 seconds from lastTime
    # This accounts for work duration and ensures precise 60-second intervals
    elapsed = time.time() - lastTime
    time.sleep(max(0, 60 - elapsed))
