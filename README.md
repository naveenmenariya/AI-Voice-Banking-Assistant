# Kentiq AI Voice Banking Assistant Dubai Bank

## Project Overview
This project is a voice-enabled AI banking assistant. It takes voice input from the user and responds using speech. It can check account balance, transfer money, validate cheque images, perform KYC, and show transaction history using dummy data.

## System Requirements
Python 3.9 or higher  
Working microphone  
Speakers or headphones  
Webcam (optional for video KYC)  
Internet connection for speech recognition  

## Installation
Open terminal in your project folder and run:

pip install -r requirements.txt

If you are using Windows and pyaudio fails:

pip install pipwin  
pipwin install pyaudio  

## Running the Project
Run the following command:

python main.py

The bot will start and speak a welcome message. After that it will listen for your voice commands.

## Available Commands
You can speak the following:

What is my balance  
Transfer money  
Scan cheque  
Start KYC  
Transaction history  
Help  
Goodbye  

## Features
Voice input and voice output  
Account balance inquiry  
Money transfer with confirmation  
Cheque validation using image  
Audio and video KYC recording  
Error handling for noise and invalid input  

## Troubleshooting
If microphone is not working, check system sound settings and run:

python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

If no voice output on Linux:

sudo apt install espeak  

If webcam is not opening, close other apps using camera or try changing camera index in code.

## Notes
This project uses dummy data and does not perform real banking operations.  
KYC recordings are saved in the recordings folder.
