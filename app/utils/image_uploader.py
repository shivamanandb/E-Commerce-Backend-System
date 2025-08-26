import cloudinary
import cloudinary.uploader
from typing import Optional, Dict
from exceptions import GeneralException


async def upload_image_to_cloudinary(file_path: str, folder: Optional[str] = None) -> Dict:
    """
    Uploads an image to Cloudinary.

    Args:
        file_path (str): The local path of the image to upload.
        folder (Optional[str]): Optional folder in Cloudinary where the image should be stored.

    Returns:
        Dict: A dictionary containing Cloudinary's response, including the public URL and metadata.

    Raises:
        HTTPException: If the upload fails due to any reason (e.g., invalid file, connectivity issues).
    """
    try:
        
        options = {"resource_type": "image"}
        if folder:
            options["folder"] = folder

        # Note: cloudinary.uploader.upload is synchronous
        result = cloudinary.uploader.upload(file_path, **options)
        return result

    except Exception as e:
        raise GeneralException(status_code=500, detail=f"Image upload failed: {str(e)}")
