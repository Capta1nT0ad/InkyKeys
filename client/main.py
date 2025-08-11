from io import BytesIO
import json
import sys
import os
from pathlib import Path
import logging
import signal

from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import dotenv_values
from mac_notifications import client
from read import capture_touch
from keystroke import send_string


logging.basicConfig(
    level=logging.INFO,
    datefmt="%d/%m/%y %H:%M:%S",
    format="%(asctime)s (%(filename)s) [%(levelname)s]: %(message)s",
    force=True
)

logging.getLogger("google_genai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


class Format(BaseModel):
    is_char_present: bool
    chars_content: str


def main(apikey, server, notif_client):

    logging.info("Ready.")
    notif_client.create_notification(title='Ready', text="Start writing.", icon=None, sound=None, action_button_str="Quit", action_callback=lambda *_: (os.killpg(0, signal.SIGTERM), os._exit(0)))
    img = capture_touch(timeout=0.8)

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img.save('last_drawing.png')

    img = buffer.getvalue()
    buffer.close()

    logging.info("Recognising text...")
    notif_client.create_notification(title='Stand by', text="Recognising text...", icon=Path(__file__).parent / "last_drawing.png", sound=None, action_button_str="Quit", action_callback=lambda: os._exit(0))

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
            "system_instruction": """You will receive an image file containing digitally handwritten content.  
            Your task is to output a JSON object with the following fields:

            {
              "is_char_present": <boolean>,   // true if any recognisable character or special gesture is present
              "chars_content": <string>       // the interpreted text or special command
            }

            ### Detection Rules (apply in this exact order):

            1. **Special Gestures (take priority over normal character recognition)**  
                - If the image shows **only** a long, straight horizontal line across the very bottom → `"chars_content": " "`  
                - If the image shows **only** a long, straight diagonal line from one corner to the other → `"chars_content": "!BACKSPACE!"` 
                    (NOTE: This does NOT mean just "!", it means the full text "!BACKSPACE!")
                - If the image shows **only** a long, straight vertical line along the far left or far right edge → `"chars_content": "!RETURN!"`  

            2. **Normal Character Recognition**  
               - If letters, numbers, punctuation, or symbols are present, output them in reading order.  
               - Preserve all spaces between words. Do **not** add a space at the end.  
               - If there are multiple lines, combine them in order from top to bottom, inserting a single space between lines.  
               - There may also be single punctuation, e.g. ",", "." or "!". Output the punctuation as usual.

            3. **Empty or Unintelligible Image**  
               - If no recognisable characters or gestures are present →  
                 `"is_char_present": false` and `"chars_content": ""`  

            ### Examples:

            **Example 1**  
            Image text:  
                `This is` (top line)  
                `a test` (bottom line)  
            → Output:  
            ```json
            {"is_char_present": true, "chars_content": "This is a test"}
            ```

            **Example 2**  
            Image text:  
                `Example text` (only line)  
            → Output:  
            ```json
            {"is_char_present": true, "chars_content": "This is a test"}
            ```

            **Example 3**  
            Image text:  
                `A` (only line)  
            → Output:  
            ```json
            {"is_char_present": true, "chars_content": "A"}
            ```

            **Example 4**  
            Image content: ONLY a long straight line across the bottom edge
            → Output:  
            ```json
            {"is_char_present": true, "chars_content": " "}
            ```

            **Example 5**  
            Image content: ONLY a long diagonal line corner-to-corner
            → Output:  
            ```json
            {"is_char_present": true, "chars_content": "!BACKSPACE!"} 
            ``` (DO NOT interpret as !, then backspace, then ! leaving only "!", rather it is the FULL TEXT "!BACKSPACE!")
            
            **Example 6**  
            Image content: ONLY a long straight line across the far right edge
            → Output:  
            ```json
            {"is_char_present": true, "chars_content": "!RETURN!"}
            ```

            """,
            "response_mime_type": "application/json",
            "response_schema": list[Format],
        }
    )

    out_data = response.text

    out_data = json.loads(out_data)
    if out_data[0]["is_char_present"]:
        letters = out_data[0]["chars_content"]
        notif_client.create_notification(title='Typing...',text=f"'{letters}'", icon=Path(__file__).parent / "last_drawing.png", sound=None, action_button_str="Quit", action_callback=lambda: os._exit(0))
        logging.info("Found text! >> '%s'", letters)
        send_string(letters, server)
        
    else:
        logging.info("Did not find any text.")

    print()


if __name__ == "__main__":

    try:
        config = dotenv_values(Path("~/.config/inkykeys.env").expanduser())
        apikey = config["API_KEY"]
        server = config["KEYSTROKE_SERVER"]

        while True:
            main(apikey, server, client)
    
    except Exception as e:
        logging.exception("Unhandled exception! %s.", e)
        client.create_notification(title='Fatal error', text=str(e), sound=None)
        os.killpg(os.getpid(), signal.SIGABRT)