# py-apex-legends

A Python app to track your apex legends stats using the [Apex Legends Status API](https://apexlegendsstatus.com/)

## Installation

- Install Python 3.6+
- Install requests (`pip install requests`)
- Configure the program (see [configuration](#Configuration))
- Run the program with `python tracker.py`
    - If you want to run it headless (no console) run it with `pythonw` instead

## Configuration

You can get an API key [here](https://apexlegendsapi.com/index.php), **Do not spam the API with reloads!** Your token _will_ get banned.  
Copy this template to a file named `settings.json` and change the values to fit your info.  
Make sure it's in the same folder as `tracker.py`!

```json
{
    "token": "YOUR_API_TOKEN",
    "username": "YOUR_PLATFORM_USERNAME",
    "platform": "YOUR_PLATFORM"
}
```

## A note regarding kills and damage (and other future tracked stats)

The stats tracked by the API (and all other apex legends APIs) are only updated based on trackers for your **currently equipped legend**

Totals will likely be wrong for you. If you want to update the API to get the correct numbers, do the following:
1. Equip damage and kill trackers on each legend. 
2. Go through each legend one by one and only swap legends when you see the number in the application update. If it doesn't change after 15 seconds, it likely already was added to the database and you can move on to the next one.
3. To keep the trackers up to date, leave the application running while you play and at the end of each game, the totals should update after a few seconds in the lobby.
