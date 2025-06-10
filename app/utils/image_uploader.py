import cloudinary
import cloudinary.uploader


async def upload_image_to_cloudinary(file_path: str, folder: str = None):
    """
    Upload image to Cloudinary.
    """
    
    options = {"resource_type": "auto"}
    if folder:
        options["folder"] = folder
    result = cloudinary.uploader.upload(file_path, **options)
    return result
