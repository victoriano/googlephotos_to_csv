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
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path,
                                                             ["https://www.googleapis.com/auth/photoslibrary.readonly"])
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())

    return build("photoslibrary", "v1", credentials=creds, static_discovery=False)


def download_photos(api, folder_path, num_photos, download_images=True, resolution=None):
    try:
        os.makedirs(folder_path, exist_ok=True)

        next_page_token = ""
        page_size = min(num_photos, 100)
        items = []  # Initialize items here
        urls = []   # Initialize urls here too, for consistency
        while num_photos > 0:
            results = api.mediaItems().search(
                body={
                    "pageSize": page_size,
                    "pageToken": next_page_token,
                    "filters": {
                        "includeArchivedMedia": False,
                        "featureFilter": {
                            "includedFeatures": ["FAVORITES"]
                        }
                    }
                }
            ).execute()

            items = results.get("mediaItems", [])

            for item in items:

                print(f"Getting data from {item['filename']}...")

                url = item["baseUrl"]
                if resolution:
                    url += f"=w{resolution}"

                urls.append(url)

                if download_images:
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
                                continue
                    else:
                            print(f"Cannot save {item['filename']}: unsupported file format")
                            continue

                num_photos -= 1
                if num_photos <= 0:
                    break

            next_page_token = results.get("nextPageToken", "")
            if not next_page_token:
                break

        return items, urls

    except HttpError as error:
        print(f"An error occurred: {error}")
        return

    
def main(num_photos_to_download, download_images, resolution):
    # Set the output folder
    output_folder = "downloaded_photos"

    google_photos_api = setup_google_photos_api()
    items, urls = download_photos(google_photos_api, output_folder, num_photos_to_download, download_images, resolution)

    create_metadata_csv(output_folder, items, urls)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download photos from Google Photos.')
    parser.add_argument('-n', '--num_photos', type=int, default=10, help='Number of photos to download')
    parser.add_argument('-d', '--download', action='store_true', help='Download photos')
    parser.add_argument('-r', '--resolution', type=str, help='Resolution for downloaded photos')

    args = parser.parse_args()

    #python main.py -n 4 -d -r 3000
    #python main.py -n 4
    main(args.num_photos, args.download, args.resolution)