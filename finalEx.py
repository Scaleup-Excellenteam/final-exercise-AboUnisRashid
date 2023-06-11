import json
import os
import re
import time
import asyncio

import openai
import pptx

EXIT_SUCCESS = 0
CONTENT = [
    {"role": "system", "content": "Can you explain the slides in basic English, and provide examples if needed!"}
]
ERROR_MESSAGE = "Something is wrong:"
ENGINE_MODEL = "gpt-3.5-turbo"
WRITE_TO_FILE_MODE = 'w'


async def parse_file_to_slides(file_path):
    # Parses a PowerPoint file and extracts the content of each slide
    ppt = await asyncio.to_thread(pptx.Presentation, file_path)
    slides = []

    for slide in ppt.slides:
        slide_content = []

        for shape in slide.shapes:
            if shape.has_text_frame:
                text_frame = shape.text_frame
                for paragraph in text_frame.paragraphs:
                    for run in paragraph.runs:
                        slide_content.append(run.text)

        slides.append(slide_content)

    return slides


async def explain_slides(slides):
    # Generates explanations for each slide using the OpenAI API
    explanations = []

    for slide in slides:
        explanation = await parse_slide_of_pptx(slide)
        explanations.append(explanation)

    return explanations


async def parse_slide_of_pptx(slide):
    # Parses the content of a slide and sends it to the OpenAI API for completion
    try:
        response = await request_completion(slide)
        return response
    except Exception as error:
        error_message = f"{ERROR_MESSAGE} Error processing slide: {str(error)}"
        return error_message


async def request_completion(slide):
    # Sends the slide content to the OpenAI API for completion and returns the generated response
    CONTENT.append({"role": "user", "content": " ".join(slide)})
    try:
        response = openai.ChatCompletion.create(
            model=ENGINE_MODEL,
            messages=CONTENT
        )
        content = response["choices"][0].message.content
        cleaned_text = re.sub(r"[\n\r]", "", content).encode("ascii", "ignore").decode("utf-8")
        return cleaned_text.strip()
    except Exception as error:
        print(f"Error during completion request: {str(error)}")
        return None


def modify_file(explanations, presentation_path):
    # Modifies the file to store the slide explanations in a JSON format
    try:
        presentation_name = os.path.basename(presentation_path)
        presentation_name = os.path.splitext(presentation_name)[0]
        output_file = f"{presentation_name}_explanations.json"

        slide_explanations = {f"slide{slide_num}": explanation for slide_num, explanation in enumerate(explanations, start=1)}

        with open(output_file, WRITE_TO_FILE_MODE) as file:
            json.dump(slide_explanations, file, indent=4)
        print(f"Explanations saved to {output_file}")
    except FileNotFoundError as error:
        print(f"{ERROR_MESSAGE} Error saving explanations: {str(error)}")


async def activate_main():
    # Orchestrates the main flow of the program
    presentation_path = "Presentation_Path"  # Specify the path to your PowerPoint presentation
    print("Processing PowerPoint...")
    start_time = time.time()

    slides = await parse_file_to_slides(presentation_path)
    explanations = await explain_slides(slides)
    modify_file(explanations, presentation_path)

    end_time = time.time()
    execution_time = end_time - start_time
    minutes, seconds = divmod(execution_time, 60)
    print(f"Execution time: {minutes:.0f} minutes {seconds:.2f} seconds")


async def main():
    openai.api_key = 'API-KEY'  # Replace with your OpenAI API key
    await activate_main()
    return EXIT_SUCCESS


if __name__ == "__main__":
    asyncio.run(main())
