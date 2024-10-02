from pydantic import BaseModel


class ScreenshotBase(BaseModel):
    url: str
    s3_path: str


class Screenshot(ScreenshotBase):
    id: int

    class Config():
        from_attributes = True
        