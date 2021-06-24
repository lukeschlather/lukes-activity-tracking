# Setup
Prerequisites

```
sudo apt-get -y install python3-pip
pip3 install poetry
```

Create a file secrets.bash with:
```
export GOOGLE_MAPS_API_KEY='<>'
```

Run with:

```
. secrets.bash
poetry run python generate_heatmap.py --folder-root <>
```

# Exploring

To explore the contents of the fitfile's messages, enter this into a debugger:
```
    i = 0
    print(i); fitfile.messages[i]; i+=1
```

The messages don't seem to be guaranteed to be in any order. I noticed the
message which contains the sport is usually at position 17, however sometimes
not.

# Credits

This is partially lifted from https://github.com/TomCasavant/GPXtoHeatmap but it
reads directly from .fit files rather than needing to be converted into GPX. (I
tried to use a fit-gpx converter but the converter stripped out a lot of
interesting information including the activity sport.)
