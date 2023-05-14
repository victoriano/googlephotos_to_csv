import os
import json
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PIL import Image
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


import imageio
from PIL import Image

def download_photos(api, folder_path, num_photos):
    try:
        os.makedirs(folder_path, exist_ok=True)

        next_page_token = ""
        page_size = min(num_photos, 100)
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
                print(f"Downloading {item['filename']}...")

                url = item["baseUrl"]
                url += "=w1800"

                response = requests.get(url)
                file_ext = os.path.splitext(item["filename"])[1]

                if file_ext.lower() in [".jpg", ".png"]:
                    image = Image.open(BytesIO(response.content))
                    image.save(os.path.join(folder_path, item["filename"]))
                elif file_ext.lower() == ".dng":
                    try:
                        img_data = imageio.imread(BytesIO(response.content))
                        output_filename = os.path.splitext(item["filename"])[0] + ".png"  # Convert DNG to PNG
                        imageio.imsave(os.path.join(folder_path, output_filename), img_data)
                    except Exception as e:
                        print(f"Error processing {item['filename']}: {e}")
                        continue
                elif file_ext.lower() == ".heic":
                    print(f"Skipping {item['filename']}: HEIC format not supported")
                    continue
                else:
                    print(f"Cannot save {item['filename']}: unsupported file format")
                    continue


                if "mediaMetadata" in item:
                    exif_filename = os.path.splitext(item["filename"])[0] + "_exif.json"
                    exif_filepath = os.path.join(folder_path, exif_filename)
                    with open(exif_filepath, "w") as exif_file:
                        json.dump(item["mediaMetadata"], exif_file, indent=2)

                num_photos -= 1
                if num_photos <= 0:
                    break

            next_page_token = results.get("nextPageToken", "")
            if not next_page_token:
                break

        return items

    except HttpError as error:
        print(f"An error occurred: {error}")
        return

    
def main():
    # Set the output folder and number of photos to download
    output_folder = "downloaded_photos"
    num_photos_to_download = 10

    google_photos_api = setup_google_photos_api()
    items = download_photos(google_photos_api, output_folder, num_photos_to_download)

    create_metadata_csv(output_folder, items)

if __name__ == "__main__":
    main()