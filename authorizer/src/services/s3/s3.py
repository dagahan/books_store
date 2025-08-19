from src.core.config import ConfigLoader
from src.core.utils import EnvTools
from aiobotocore.session import get_session as get_s3_session
from botocore.config import Config
from contextlib import asynccontextmanager
from typing import Optional
import os
import mimetypes
import uuid


class S3Client:
    def __init__(self) -> None:
        self.bucket_name = EnvTools.load_env_var("s3_bucket_name")
        self.s3_config = {
            "aws_access_key_id": EnvTools.load_env_var("s3_access_key"),
            "aws_secret_access_key": EnvTools.load_env_var("s3_secret_key"),
            "endpoint_url": EnvTools.load_env_var("s3_endpoint_url"),
        }
        self.s3_session = get_s3_session()
        self.botocore_config = Config(
            region_name=EnvTools.load_env_var("s3_region"),
            s3={"addressing_style": "virtual"},
            proxies={"http": None, "https": None},
            retries={"max_attempts": 3, "mode": "standard"},
        )
        self.verify = False

    
    @asynccontextmanager
    async def get_s3_client(self):
        async with self.s3_session.create_client(
            "s3",
            **self.s3_config,
            config=self.botocore_config,
            verify=self.verify,
        ) as client:
            yield client


    async def upload_bytes(
        self,
        data: bytes,
        key: str,
        content_type: Optional[str] = None
    ) -> None:
        kwargs = {"Bucket": self.bucket_name, "Key": key, "Body": data}
        if content_type:
            kwargs["ContentType"] = content_type
        async with self.get_s3_client() as s3:
            await s3.put_object(**kwargs)


    def make_key(
        self,
        user_id: str,
        filename: str,
        content_type: Optional[str]
    ) -> str:
        ext = os.path.splitext(filename or "")[1]
        if not ext:
            ext = mimetypes.guess_extension(content_type or "") or ".jpg"
        return f"avatars/{user_id}/{uuid.uuid4().hex}{ext.lower()}"


    async def upload_file(
        self,
        file_path: str,
        object_name: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> str:
        key = object_name or os.path.basename(file_path)
        ctype = content_type or mimetypes.guess_type(file_path)[0]
        async with self.get_s3_client() as s3:
            with open(file_path, "rb") as f:
                body = f.read()
            kwargs = {"Bucket": self.bucket_name, "Key": key, "Body": body}
            if ctype:
                kwargs["ContentType"] = ctype
            await s3.put_object(**kwargs)
        return key


    async def delete_object(
        self,
        key: str
    ) -> None:
        async with self.get_s3_client() as s3:
            await s3.delete_object(Bucket=self.bucket_name, Key=key)


