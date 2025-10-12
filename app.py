import streamlit as st
import boto3
import uuid

# ✅ Load AWS credentials from Streamlit Secrets
AWS_ACCESS_KEY = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
REGION = st.secrets["AWS_REGION"]
BUCKET = st.secrets["S3_BUCKET"]

# Configure S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
)

st.title("📸 Upload Images to S3")

# File uploader
uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Give file a unique name to avoid overwriting
    file_key = f"{uuid.uuid4()}_{uploaded_file.name}"

    try:
        # Upload to S3
        s3.upload_fileobj(uploaded_file, BUCKET, file_key)
        st.success(f"✅ Uploaded as {file_key}")

        # Display the uploaded image from S3
        image_url = f"https://{BUCKET}.s3.{REGION}.amazonaws.com/{file_key}"
        st.image(image_url, caption="Uploaded Image", use_column_width=True)

    except Exception as e:
        st.error(f"Error uploading file: {e}")
