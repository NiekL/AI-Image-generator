import os
from dotenv import load_dotenv
from openai import OpenAI
import requests

# Load environment variables from the .env file
load_dotenv()

# Initialize OpenAI API key
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OpenAI API key not found. Please set it in the .env file.")

# Initialize OpenAI client with API key
client = OpenAI(api_key=API_KEY)

# Function to read descriptions from a .txt file
def read_descriptions(file_path):
    try:
        with open(file_path, 'r') as file:
            descriptions = file.readlines()
        return [desc.strip() for desc in descriptions if desc.strip()]
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return []
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

# Function to generate and save an image
def generate_image(prompt, output_folder, image_num):
    try:
        print(f"\nGenerating image {image_num} for prompt: '{prompt}'...")

        # Generate image using DALL-E 3 API
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        # Validate API response
        if not response.data or not response.data[0].url:
            raise ValueError("Invalid response from DALL-E API")

        # Get the image URL from the API response
        image_url = response.data[0].url

        # Download the image
        image_data = requests.get(image_url)
        if image_data.status_code != 200:
            raise ValueError(f"Failed to download image from {image_url}")

        # Save the image to the output folder
        image_path = os.path.join(output_folder, f"image_{image_num}.png")
        with open(image_path, 'wb') as img_file:
            img_file.write(image_data.content)

        print(f"Image {image_num} generated and saved to {image_path}")

    except Exception as e:
        print(f"Error generating image for prompt '{prompt}': {e}")

# Main function to execute the script
def main():
    descriptions_file = 'descriptions.txt'
    output_folder = 'generated_images'

    # Create output directory if it doesn't exist
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    except Exception as e:
        print(f"Error creating output directory: {e}")
        return

    # Read descriptions from the text file
    descriptions = read_descriptions(descriptions_file)
    if not descriptions:
        print("No descriptions found. Exiting.")
        return

    print(f"\nStarting image generation for {len(descriptions)} prompts...\n")

    # Loop through each description and generate an image
    for i, prompt in enumerate(descriptions):
        generate_image(prompt, output_folder, i + 1)

    print("\nAll images generated successfully.")

if __name__ == "__main__":
    main()
