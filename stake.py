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
                
                # Process images after downloading
                extract_text_from_image(language='eng+spa')

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

def preprocess_image(image_path, save_preprocessed=False):
    """Load and preprocess the image for better OCR results: remove watermark but keep colored text."""
    # Load the image using OpenCV
    img_cv = cv2.imread(image_path)

    # Convert to grayscale for watermark detection
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    ret3, th3 = cv2.threshold(blur, 200, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Convert to PIL Image
    final_image = Image.fromarray(th3)
    
    os.remove(image_path)  # Remove original image after processing

    # Save the preprocessed image if required
    if save_preprocessed:
        preprocessed_image_path = os.path.join(output_dir, os.path.basename(image_path))
        final_image.save(preprocessed_image_path)

    return final_image

def extract_text_from_image(language: str = 'eng+spa'):
    """Extract text from images in the specified directory and save to a file."""
    image_directory = download_dir
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    output_file_path = 'extracted_text.txt'  # Output file for extracted text

    # Create or overwrite the output file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for filename in os.listdir(image_directory):
            if filename.lower().endswith(image_extensions):
                image_path = os.path.join(image_directory, filename)
                try:
                    # Preprocess the image and save
                    preprocess_image(image_path, save_preprocessed=True)

                    # Extract text using pytesseract
                    custom_config = r'--oem 3 --psm 6'  # Adjust Tesseract settings as needed
                    extracted_text = pytesseract.image_to_string(image_path, lang=language, config=custom_config)
                    
                    os.remove(image_path)  # Remove preprocessed image after processing
                    
                    # Save the extracted text to the output file
                    output_file.write(f'>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<\n')
                    output_file.write(f'Extracted from: {filename}\n')
                    output_file.write(extracted_text + '\n')
                    output_file.write(f'>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<\n\n')

                    print(f"Image '{image_path}' successfully processed.")
                except Exception as e:
                    print(f"An error occurred while processing '{image_path}': {e}")

if __name__ == '__main__':
    # Path to the tesseract executable (required on Windows)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # Run the main function
    asyncio.run(main())
