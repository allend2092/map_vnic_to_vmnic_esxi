from datetime import datetime

# Generate a timestamp for now
now = datetime.now()
print(now) # 2022-01-30 16:13:49.123456

# Generate a timestamp for 24 hours ago
previous = now - datetime.timedelta(hours=24)
print(previous) # 2022-01-29 16:13:49.123456

# Compare the timestamps
if previous < now:
    print("Previous timestamp is older than now")
else:
    print("Previous timestamp is not older than now")

# Check if the previous timestamp is 24 hours older than now
if (now - previous).total_seconds() >= 86400:
    print("Previous timestamp is 24 hours older than now")
    # Take some action
else:
    print("Previous timestamp is not 24 hours older than now")
