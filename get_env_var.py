import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the LOGO_IMG variable
logo_img = os.getenv("LOGO_IMG", "images/generic_logo.png")

# Print the value of LOGO_IMG for the batch file to capture
print(logo_img)
