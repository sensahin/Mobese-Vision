from selenium import webdriver
from openai import OpenAI
import boto3
import time

# Replace with your actual OpenAI API key and AWS credentials
openai_api_key = ''
aws_access_key_id = ''
aws_secret_access_key = ''
s3_bucket_name = ''

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# URL of the live camera feed
fullurl = 'https://webcams.windy.com/webcams/stream/1494608365'

# Selenium WebDriver setup
op = webdriver.ChromeOptions()
op.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
op.add_argument('headless')
driver = webdriver.Chrome(options=op)
driver.get(fullurl)
time.sleep(5)

# Take a screenshot and save it in the current directory
screenshot_filename = 'screenshot.png'
driver.save_screenshot(screenshot_filename)
driver.quit()

# Initialize boto3 client
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Upload the screenshot to S3
s3_client.upload_file(screenshot_filename, s3_bucket_name, screenshot_filename)
pre_signed_url = s3_client.generate_presigned_url('get_object',
                                                  Params={'Bucket': s3_bucket_name, 'Key': screenshot_filename},
                                                  ExpiresIn=60)
s3_image_url = f'https://{s3_bucket_name}.s3.amazonaws.com/{screenshot_filename}'


# Analyze the image using OpenAI's GPT-Vision
response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What’s in this image? Respond in Turkish."},
                {"type": "image_url", "image_url": pre_signed_url},
            ],
        }
    ],
    max_tokens=300,
)

# Print the response
print(response.choices[0].message.content)
