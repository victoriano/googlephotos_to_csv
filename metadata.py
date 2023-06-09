import os
import csv

def create_metadata_csv(folder_path, items, urls):
    csv_filename = "metadata.csv"
    csv_filepath = os.path.join(folder_path, csv_filename)
    with open(csv_filepath, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow(["Filename", "File Type", "Creation Time", "Width", "Height", "Camera Make", "Camera Model", "Focal Length", "Aperture", "ISO Equivalent", "Exposure Time", "Url"])

        for item, url in zip(items, urls):
            if "filename" not in item:
                continue

            filename = item["filename"]
            file_type = os.path.splitext(filename)[1][1:]  # Get file extension without dot
            metadata = item.get("mediaMetadata", {})

            creation_time = metadata.get("creationTime", "")
            width = metadata.get("width", "")
            height = metadata.get("height", "")

            photo_metadata = metadata.get("photo", {})
            camera_make = photo_metadata.get("cameraMake", "")
            camera_model = photo_metadata.get("cameraModel", "")
            focal_length = photo_metadata.get("focalLength", "")
            aperture_f_number = photo_metadata.get("apertureFNumber", "")
            iso_equivalent = photo_metadata.get("isoEquivalent", "")
            exposure_time = photo_metadata.get("exposureTime", "")
            if exposure_time.endswith('s'):
                exposure_time = exposure_time[:-1]

            writer.writerow([filename, file_type, creation_time, width, height, camera_make, camera_model, focal_length, aperture_f_number, iso_equivalent, exposure_time, url])