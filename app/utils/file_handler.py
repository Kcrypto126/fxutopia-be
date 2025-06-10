import os
import uuid
import aiofiles
from PIL import Image
from fastapi import UploadFile, HTTPException
from typing import List, Optional
from app.config import get_settings

settings = get_settings()

class FileHandler:
    def __init__(self):
        self.upload_folder = settings.UPLOAD_FOLDER
        self.max_file_size = settings.MAX_FILE_SIZE
        
        # Allowed file types
        self.allowed_image_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        self.allowed_document_types = ["application/pdf", "application/zip", "application/x-zip-compressed"]
        
    async def save_upload_file(
        self, 
        file: UploadFile, 
        folder: str,
        allowed_types: Optional[List[str]] = None
    ) -> str:
        """Save uploaded file and return the file path"""
        
        # Validate file type
        if allowed_types and file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not allowed"
            )
        
        # Check file size
        contents = await file.read()
        if len(contents) > self.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {self.max_file_size} bytes"
            )
        
        # Generate unique filename
        file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
        filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
        
        # Create directory if it doesn't exist
        folder_path = os.path.join(self.upload_folder, folder)
        os.makedirs(folder_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(folder_path, filename)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(contents)
        
        # Reset file position
        await file.seek(0)
        
        return f"/{folder}/{filename}"
    
    async def save_image(self, file: UploadFile, folder: str, resize: Optional[tuple] = None) -> str:
        """Save image file with optional resizing"""
        file_path = await self.save_upload_file(file, folder, self.allowed_image_types)
        
        if resize:
            full_path = os.path.join(self.upload_folder, file_path.lstrip("/"))
            await self.resize_image(full_path, resize)
        
        return file_path
    
    async def resize_image(self, file_path: str, size: tuple):
        """Resize image to specified dimensions"""
        try:
            with Image.open(file_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(file_path, optimize=True, quality=85)
        except Exception as e:
            print(f"Error resizing image: {e}")
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        try:
            full_path = os.path.join(self.upload_folder, file_path.lstrip("/"))
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        except Exception:
            return False