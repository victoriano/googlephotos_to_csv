# Google Photos Downloader

## SYNOPSIS

`google_photos_downloader.py [-n NUM_PHOTOS] [-d] [-r RESOLUTION]`

## DESCRIPTION

This script allows you to download your Google Photos, optionally at a custom resolution, and generates a CSV file with metadata for each photo. It can also handle HEIC files, but does not convert them to JPEG by default.

## OPTIONS

`-n, --num_photos NUM_PHOTOS`
: The number of photos to download. Defaults to 100.

`-d, --download`
: Include this flag to download the photos. If not included, the script will only generate metadata.

`-r, --resolution RESOLUTION`
: The width in pixels of the downloaded photos. If not specified, photos will be downloaded at their original resolution.

## EXAMPLES

`python google_photos_downloader.py --num_photos 200 --download --resolution 3000`
: This command will download 200 photos with a width of 3000 pixels.

`python google_photos_downloader.py --num_photos 100`
: This command will generate metadata for 100 photos, but will not download the photos.

## NOTES

This script requires the `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`, `Pillow`, and `imageio` libraries.

## AUTHOR

Written by Victoriano Izquierdo. You can reach out to him on Twitter [@victorianoi](https://twitter.com/victorianoi).

## REPORTING BUGS

Report bugs to Victoriano Izquierdo via Twitter [@victorianoi](https://twitter.com/victorianoi).

## COPYRIGHT

Copyright © 2023 Victoriano Izquierdo. License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>. This is free software: you are free to change and redistribute it. There is NO WARRANTY, to the extent permitted by law.
