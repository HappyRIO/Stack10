import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto
from PIL import Image
import pytesseract
import cv2
import numpy as np
from dotenv import load_dotenv

load_dotenv()
# Set up your API credentials
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
channel_username = os.getenv('CHANNEL_USERNAME')
special_text = os.getenv('SPECIFIC_TEXT')

# Create directories to save downloaded and preprocessed images
download_dir = 'downloads'
output_dir = 'preprocessed'
os.makedirs(download_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

async def main():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        # Retrieve the channel
        channel = await client.get_entity(channel_username)

        # Event handler for new messages in the channel
        @client.on(events.NewMessage(chats=channel))
        async def handler(event):
            message = event.message
            
            # Print the message text for visibility
            print(f'Message: {message.message}')

            # Check if the message contains the special text
            if special_text in message.message:
                next_message = await client.get_messages(channel, ids=message.id + 1)
                if next_message:
                    print(f'Image: {next_message.message}')
                    await download_images(next_message, client)            

        # Run the client until interrupted
        print(f'Listening for new messages in {channel_username}...')
        await client.run_until_disconnected()

async def download_images(message, client):
    if message.media:
        if isinstance(message.media, MessageMediaPhoto):
            # Download the image from a photo message directly
            file_path = os.path.join(download_dir, f'{message.id}.jpg')
            await client.download_media(message.media, file=file_path)
            print(f'Downloaded: {file_path}')
            
            extract_text_from_image(file_path, language='eng+spa')

def preprocess_image(image_path):
    """Load and preprocess the image for better OCR results."""
    img_cv = cv2.imread(image_path)

    # Convert to grayscale and apply Gaussian blur
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    ret, threshed = cv2.threshold(blur, 200, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Save the preprocessed image
    preprocessed_path = os.path.join(output_dir, os.path.basename(image_path))
    cv2.imwrite(preprocessed_path, threshed)

    return preprocessed_path

def extract_text_from_image(file_path, language: str = 'eng+spa'):
    """Extract text from images in the specified directory and save to a file."""
    output_file_path = 'extracted_text.txt'  # Output file for extracted text

    # Create or overwrite the output file
    with open(output_file_path, 'a', encoding='utf-8') as output_file:  # Append mode
                try:
                    # Preprocess the image and get the path of the preprocessed image
                    preprocessed_image_path = preprocess_image(file_path)

                    # Extract text using pytesseract
                    custom_config = r'--oem 3 --psm 6'
                    extracted_text = pytesseract.image_to_string(preprocessed_image_path, lang=language, config=custom_config)

                    # Save the extracted text to the output file
                    output_file.write(f'>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<\n')
                    output_file.write(f'Extracted from: {file_path}\n')
                    output_file.write(extracted_text + '\n')
                    output_file.write(f'>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<\n\n')

                    print(f"Image '{file_path}' successfully processed.")
                except Exception as e:
                    print(f"An error occurred while processing '{file_path}': {e}")

                # Optionally, remove the downloaded image after processing
                os.remove(file_path)
                os.remove(preprocessed_image_path)

if __name__ == '__main__':
    # Update the Tesseract command based on your OS and installation path
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust as needed

    # Run the main function
    asyncio.run(main())
