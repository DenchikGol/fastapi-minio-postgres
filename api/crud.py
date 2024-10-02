from sqlalchemy.orm import Session
from api import models


def get_screenshot(db: Session, site_url: str):
    return db.query(models.Screenshot).filter(models.Screenshot.url == site_url).first()
    

def create_path_to_screenshot(db: Session, site_url: str, s3_path: str):
    screenshot_path = models.Screenshot(url=site_url, s3_path = s3_path)
    db.add(screenshot_path)
    db.commit()
    db.refresh(screenshot_path)
    return screenshot_path
