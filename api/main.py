from os import environ
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import Annotated
from minio import Minio
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from starlette.responses import StreamingResponse
from api import models, schemas, crud
from api.database import engine, get_db
from sqlalchemy.orm import Session


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_minio_client():
    host = environ.get("MINIO_HOST", "minio")
    port = environ.get("MINIO_PORT", "9000")
    a_key = environ.get("MINIO_ROOT_USER", "minioadmin")
    s_key = environ.get("MINIO_ROOT_PASSWORD", "minioadmin")
    s3_client = Minio(
        endpoint="minio:9000",
        secret_key="minioadmin",
        access_key="minioadmin",
        secure=False
    )
    return s3_client

# Настройка Selenium driver
def get_selenium_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    driver = webdriver.Remote(
        command_executor="http://selenium:4444/wd/hub",
        options=options,
    )
    return driver


@app.post("/screenshot", response_model=schemas.Screenshot)
def screenshot(site_url: str, db: Annotated[Session, Depends(get_db)], is_fresh: bool = False):
    screenshot_object = crud.get_screenshot(db, site_url)
    s3_client = get_minio_client()
    s3_bucket = "screenshots"
    if not is_fresh and screenshot_object:
        db.close()
        return StreamingResponse(s3_client.get_object(
                s3_bucket,
                screenshot_object.s3_path
            ),
            media_type="image/png"
        )
        

    # Создание скриншота
    driver = get_selenium_driver()
    
    try:
        driver.get(site_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        screenshot_path = f"/tmp/screenshot_{site_url.replace('https://', '').replace('http://', '').replace('.', '_').replace('/', '_')}.png"
        driver.save_screenshot(screenshot_path)
    except TimeoutException:
        db.close()
        return HTTPException(status_code=404, detail=f"Url is incorrect. Site with {site_url} not found")


    
    # Загрузка в S3
    if not s3_client.bucket_exists(s3_bucket):
        s3_client.make_bucket(s3_bucket)
    
    s3_client.fput_object(
        bucket_name=s3_bucket,
        object_name=screenshot_path,
        content_type="image/png",
        file_path=screenshot_path
    )

    
    # Сохранение в базе данных
    if not screenshot_object:
        crud.create_path_to_screenshot(db, site_url, screenshot_path)
    db.close()
    driver.quit()
    return FileResponse(screenshot_path)
