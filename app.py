import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError
import uuid

# Load secrets
import os
AWS_ACCESS_KEY = st.secrets["AKIAQIZB4WMEXA43T3WH"]
AWS_SECRET_KEY = st.secrets["gC17UhZoqv7U91efqOjt1WstKiog+17UfV8nhfi"]
REGION = st.secrets["eu-west-2"]
BUCKET = st.secrets["streamlit-uploader-oct25"]

# Configure boto3
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
)

st.title("📸 Image Uploader")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Give the file a unique name
    file_key = f"{uuid.uuid4()}_{uploaded_file.name}"

    try:
        s3.upload_fileobj(uploaded_file, BUCKET, file_key)
        st.success(f"✅ Uploaded to S3 as {file_key}")

        # Optional: show image
        image_url = f"https://{BUCKET}.s3.{REGION}.amazonaws.com/{file_key}"
        st.image(image_url)

    except NoCredentialsError:
        st.error("AWS credentials not found")
