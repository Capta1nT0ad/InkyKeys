from io import BytesIO
import json

from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import dotenv_values

from read import capture_touch
from keystroke import send_string


class Format(BaseModel):
    is_char_present: bool
    chars_content: str


def main(apikey, server):

    print("start writing")
    img = capture_touch(timeout=0.5)
    print("stand by\n")

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img.save('last_drawing.png')

    img = buffer.getvalue()
    buffer.close()

    client = genai.Client(api_key=apikey)

    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        # gemini-2.0-flash-lite offers 30 rpm at 200 rpd.
        # gemini-2.5-flash-lite offers 15 rpm at 1000 rpd.
        contents=[
          types.Part.from_bytes(
            data=img,
            mime_type='image/png',
          ),
        ],
        config={
            "system_instruction": """You will receive an image file with digitally handwritten content.
            Write using the json schema whether characters are present and the string which the characters are.
            If the user writes a long straight line across the very bottom, output that there is a character present and for the string write a space as in " ".
            If the user writes a long diagonal line from one corner to another, output that there is a character present and for the string write "!BACKSPACE!".
            If the user writes a long straight line across the very right or left sides, output that there is a character present and for the string write "!RETURN!".
            However, do not mistake these for dashes, underscores or slashes et cetera.""",
            "response_mime_type": "application/json",
            "response_schema": list[Format],
        }
    )

    out_data = response.text

    out_data = json.loads(out_data)
    if out_data[0]["is_char_present"]:
        letters = out_data[0]["chars_content"]
        print(letters)
        send_string(letters, server)
        
    else:
        print(None)

    print()


if __name__ == "__main__":

    config = dotenv_values(".env")
    apikey = config["API_KEY"]
    server = config["KEYSTROKE_SERVER"]

    while True:
        main(apikey, server)