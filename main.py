import os
import json
import requests
import argparse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PIL import Image
import imageio
from io import BytesIO
from metadata import create_metadata_csv

# Set up Google Photos API
def setup_google_photos_api():
    creds = None
    token_path = "token.json"
    credentials_path = "credentials.json"

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path,
                ["https://www.googleapis.com/auth/photoslibrary.readonly"]
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())

    return build("photoslibrary", "v1", credentials=creds, static_discovery=False)

def get_photo_url(item, resolution=None):
    url = item["baseUrl"]
    if resolution:
        url += f"=w{resolution}"
    return url

def download_photo(url, item, folder_path):
    print(f"Downloading {item['filename']}...")
    response = requests.get(url)
    file_ext = os.path.splitext(item["filename"])[1]
    if file_ext.lower() in [".jpg", ".png", ".heic"]:
        with open(os.path.join(folder_path, item["filename"]), "wb") as img_file:
            img_file.write(response.content)
    elif file_ext.lower() == ".dng":
        try:
            img_data = imageio.imread(BytesIO(response.content))
            output_filename = os.path.splitext(item["filename"])[0] + ".png"  # Convert DNG to PNG
            imageio.imsave(os.path.join(folder_path, output_filename), img_data)
        except Exception as e:
            print(f"Error processing {item['filename']}: {e}")
    else:
        print(f"Cannot save {item['filename']}: unsupported file format")

def process_photo_items(items, download_images, camera_model, folder_path, resolution):
    urls = []
    total_items = []

    for item in items:
        photo_metadata = item.get('mediaMetadata', {}).get('photo', {})
        if camera_model and ('cameraMake' not in photo_metadata or 'cameraModel' not in photo_metadata):
            continue

        print(f"Getting data from {item['filename']}...")

        url = get_photo_url(item, resolution)
        urls.append(url)
        total_items.append(item)

        if download_images:
            download_photo(url, item, folder_path)
    return total_items, urls

def retrieve_photos(api, folder_path, num_photos, category, favorites=False, download_images=None, camera_model=None, resolution=None):
    try:
        os.makedirs(folder_path, exist_ok=True)

        next_page_token = ""
        page_size = min(num_photos, 100)
        total_items = []  # Initialize items here
        urls = []   # Initialize urls here too, for consistency

        while num_photos > 0:
            body = {
                "pageSize": page_size,
                "pageToken": next_page_token,
            }

            filters = {}

            if favorites:
                filters["includeArchivedMedia"] = False
                filters["featureFilter"] = {
                   
                    "includedFeatures": ["FAVORITES"]
                }
                body["filters"] = filters

            if category.startswith("album:"):
                body["albumId"] = category.split(':')[1]

            #Make the API call to get the photos for this iteration
            results = api.mediaItems().search(
                body=body
            ).execute()
            
            #Collect Items for this iteration
            items = []
            items = results.get("mediaItems", [])

            # Process items
            items, current_urls = process_photo_items(items, download_images, camera_model, folder_path, resolution)
            total_items.extend(items)
            urls.extend(current_urls)

            num_photos -= len(items)
            next_page_token = results.get("nextPageToken", "")
            if not next_page_token or num_photos <= 0:
                break
        
        print("Done!")
        print(len(total_items))
        return total_items, urls

    except HttpError as error:
        print(f"An error occurred: {error}")
        return [], []

def main(num_photos_to_download, category, favorites, download_images, camera_model, resolution):
    # Set the output folder
    output_folder = "downloaded_photos"

    google_photos_api = setup_google_photos_api()
    items, urls = retrieve_photos(google_photos_api, output_folder, num_photos_to_download, category, favorites, download_images, camera_model, resolution)

    create_metadata_csv(output_folder, items, urls)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download photos from Google Photos.')
    parser.add_argument('-n', '--num_photos', type=int, default=10, help='Number of photos to download')
    parser.add_argument('-c', '--category', type=str, default='library', help='Category of photos to download. Options: library, favorites, album:ALBUM_ID')
    parser.add_argument('-f', '--favorites', action='store_true', help='Download only favorite photos')
    parser.add_argument('-d', '--download', action='store_true', help='Download photos')
    parser.add_argument('-r', '--resolution', type=str, help='Resolution for downloaded photos')
    parser.add_argument('-cm', '--camera_model', action='store_true', help='Only download photos with camera model in metadata')

    args = parser.parse_args()

    main(args.num_photos, args.category, args.favorites, args.download, args.camera_model, args.resolution)