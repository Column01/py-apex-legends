# py-apex-legends

A Python app to track your apex legends stats using the [Apex Legends Status API](https://apexlegendsstatus.com/)

## Installation

- Install Python 3.6+
- Install requests (`pip install requests`)
- Configure the program (see [configuration](#Configuration))
- Run the program with `python tracker.py`

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
