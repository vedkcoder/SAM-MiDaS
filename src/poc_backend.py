from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import os
import base64
import json

root_dir = 'C:/Users/Ved Office/Desktop/SAM + MiDaS/sample_images/'
background_path = root_dir + 'rooms_backyards/'
chairs_path = root_dir + 'Chairs/'
tables_path = root_dir + 'Tables/'

def load_client():
    load_dotenv()
    client = genai.Client()

    return client

def load_image(image):
    """Load image from various sources"""

    if isinstance(image, Image.Image):
        return image

    if isinstance(image, str):
        try:
            if image.startswith('data:'):
                image = image.split(',', 1)[1]

            image = image.strip().replace('\n', '').replace('\r', '')

            image_bytes = base64.b64decode(image)
            return Image.open(BytesIO(image_bytes))

        except Exception as e:
            try:
                return Image.open(image)
            except:
                raise ValueError(f"Cannot load image: {e}")

    elif isinstance(image, bytes):
        return Image.open(BytesIO(image))

    elif hasattr(image, 'read'):
        return Image.open(image)

    else:
        raise TypeError(f"Unsupported image type: {type(image)}")


def load_image_from_base64(base64_string):

    if isinstance(base64_string, str):
        if ',' in base64_string:
            base64_string = base64_string.split(',', 1)[1]

        base64_string = base64_string.strip()

        try:
            image_bytes = base64.b64decode(base64_string)
        except:

            image_bytes = base64.urlsafe_b64decode(base64_string)
    else:
        image_bytes = base64_string

    return Image.open(BytesIO(image_bytes))

def create_image_obj_list(images):
    image_obj_list = []
    for image in images:
        image_obj_list.append(load_image(image))
    return image_obj_list

def generate_response_multiple(client, prompt, image_list):

    if len(image_list) == 2:
        image1, image2 = image_list
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[image1, image2, prompt],
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(
                    aspect_ratio='16:9'
                )
            )
        )
    elif len(image_list) == 3:
        image1, image2, image3 = image_list
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[image1, image2, image3, prompt],
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(
                    aspect_ratio='16:9'
                )
            )
        )

    return response

def generate_response_single(client, prompt, image):
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[image, prompt],
        config=types.GenerateContentConfig(
            image_config=types.ImageConfig(
                aspect_ratio='16:9'
            )
        )
    )

    return response

def generate_clear_prompt(client, user_input):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="""You are given a user prompt. Generate a two to three line structured prompt 
                                    using the user prompt which will be used for image generation.
                                    Instructions for prompt:
                                    1. Use the following template for generating the prompt: 
                                    'Create an image by adding <elements> inside <element> in <location of elements>.<Describe the scene>'
                                    2. The prompt should not add objects of its' own and use the provided objects in the prompt.
                                    Output Instructions:
                                    1. Important! = DO NOT add objects of your own. Use objects provided as images by the user.
                                    2. Create output in a dictionary format:
                                        {
                                        prompt: <prompt>,
                                        perspective: <perspective>,
                                        }
                                    3. Perspective will be None unless prompt mentions perspective
                                    4. Make sure the furniture objects are completely on the ground"""),
        contents=user_input
    )

    structured_prompt = response.text
    prompt, perspective = parse_perspective_prompt(structured_prompt)
    return prompt, perspective

def parse_perspective_prompt(prompt):
    cleaned = prompt.replace('```json', '').replace('```', '').strip()
    json_string = cleaned

    data = json.loads(json_string)
    prompt = data['prompt']
    perspective = data['perspective']

    return prompt, perspective


def generate_perspective(client, image, json_prompt):

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[image, json_prompt],
        config=types.GenerateContentConfig(
            image_config=types.ImageConfig(
                aspect_ratio='16:9'
            )
        )
    )

    return response

def extract_output(response):

    output = dict()

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            output['text'] = part.text
        elif part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            output['image'] = image

    return output

def load_catalogue():

    backgrounds = []
    chairs = []
    tables = []
    for path in os.listdir(background_path):
        backgrounds.append(background_path + path)

    for path in os.listdir(chairs_path):
        chairs.append(chairs_path + path)

    for path in os.listdir(tables_path):
        tables.append(tables_path + path)

    base64_dict = dict()
    base64_backgrounds = []
    for file in backgrounds:
        with open(file, "rb") as image:
            encoded = base64.b64encode(image.read()).decode()
            base64_backgrounds.append(f"data:image/jpeg;base64,{encoded}")
            image.close()

    base64_chairs = []
    for file in chairs:
        with open(file, "rb") as image:
            encoded = base64.b64encode(image.read()).decode()
            base64_chairs.append(f"data:image/jpeg;base64,{encoded}")
            image.close()

    base64_tables = []
    for file in tables:
        with open(file, "rb") as image:
            encoded = base64.b64encode(image.read()).decode()
            base64_tables.append(f"data:image/jpeg;base64,{encoded}")
            image.close()

    base64_dict['backgrounds'] = base64_backgrounds
    base64_dict['chairs'] = base64_chairs
    base64_dict['tables'] = base64_tables

    return base64_dict
