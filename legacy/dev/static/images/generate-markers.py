#!python3
import os, sys
import requests

url = "http://chart.apis.google.com/chart?cht=mm&chs={size}x{size}&chco={colour},{colour},000000&ext=.png"
colours = {
    "normal" : "ff0000",
    "disabled" : "cccccc",
    "highlit" : "ffff00",
    "external" : "0000ff"
}
def main():
    for zoom in range(22):
        size = 32 - ((14 - zoom) * 2)

        for status, rgb in colours.items():
            filename = "%d-%s.png" % (zoom, status)
            print(filename)
            r = requests.get(url.format(size=size, colour=rgb))
            with open(os.path.join("markers", filename), "wb") as f:
                f.write(r.content)

if __name__ == '__main__':
    main(*sys.argv[1:])
