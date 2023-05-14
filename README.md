# Google Photos Downloader and Metadata Collector

This script downloads photos from Google Photos and collects metadata.

Author: Victoriano Izquierdo ([Twitter](https://twitter.com/victorianoi))

## Prerequisites

1. Python 3
2. Google Photos API credentials (follow the [official guide](https://developers.google.com/photos/library/guides/get-started-python) to get these)
3. Libraries: `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`, `Pillow`, `imageio`, `requests`

Install the required libraries using pip:

```
pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client Pillow imageio requests
```

## Usage

```
python main.py [options]
```

### Options

- `-n` / `--num_photos`: Number of photos to download. Default is 10.
- `-c` / `--category`: Category of photos to download. Can be "library", "favorites", or "album:[ALBUM_ID]" (replace [ALBUM_ID] with the ID of the album). Default is "library".
- `-f` / `--favorites`: If set, only download favorite photos. Not applicable when downloading from a specific album.
- `-d` / `--download`: If set, download photos. If not set, only metadata will be collected.
- `-r` / `--resolution`: Resolution for downloaded photos. Specify the maximum width in pixels (height will be adjusted to maintain aspect ratio). If not set, the default resolution provided by Google Photos will be used.

### Examples

Download 20 photos from your library:

```
python main.py -n 20 -d
```

Download 10 favorite photos:

```
python main.py -n 10 -c favorites -d
```

Collect metadata for 50 photos from a specific album (replace [ALBUM_ID] with the ID of the album):

```
python main.py -n 50 -c album:[ALBUM_ID]
```

Download 30 photos from your library at a resolution of 1920 pixels wide:

```
python main.py -n 30 -d -r 1920
```

## Output

The script will create a "downloaded_photos" folder in the same directory as the script. This folder will contain the downloaded photos and a "metadata.csv" file with metadata for each photo.

---

Please replace the `[ALBUM_ID]` with the actual Album ID in the usage examples.