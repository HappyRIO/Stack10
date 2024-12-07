# Project Title

A Program to extract betting information from a Telegram channel.

The goal of this project is to automate the extraction of necessary information from a specific channel.
The channel ID is "@stake10peruanos".

# How it works:

## First, when a new message arrives, it checks if the message contains a specific text.
The message consists of two images, and only the first image has a caption text. So exactly, it is two messages.
therefore, for example, if the message ID include first image is 9131, the message ID include second image is 9132.
Because program can only search caption text, we get first message ID.
we can know the message ID include second image, and download the image using this ID.
## Second, preprocess downloaded images using opencv module.
## Finally, extract the text from preprocessed images using Tesseract-OCR.

# How to run:

## Environmet Installisation
### Requirement:
        Windows 10 64 bit
        Python 3.12.5

### First, create telegram app to get api_id  and api_hash.

In https://my.telegram.org/apps, should enter needed information.
Once App is created, copy App api_id and App api_hash.
### Next, in the project, fix env file.
Enter environment variable like api_id, api_hash, channel_username and special_text.

### And run the program.

#### Set virtual environment.
`python -m venv venv`

#### Activate the virtual environment:
`venv\Scripts\activate`

#### Install dependencies
`pip install -r requirements.txt`

#### Run the program
`python stake.py`

When program first runs , session file is created.
At that time, you need to enter phone number in the teminal of VScode.