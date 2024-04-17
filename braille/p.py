
import gradio as gr
import moviepy.editor as mp
import speech_recognition as sr
from transformers import pipeline
import traceback
import os

# Function to convert video to text
def video_to_text(video_path):
    clip = mp.VideoFileClip(video_path)
    clip.audio.write_audiofile("temp_audio.wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile("temp_audio.wav") as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Speech Recognition could not understand the audio"
        except sr.RequestError as e:
            return f"Could not request results ; {e}"

    return text

# Function to summarize text
def summarize_text(text):
    summarizer = pipeline("summarization")
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']

# Function to convert text to Braille
def text_to_braille(text):
    braille_dict = {
        'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑',
        'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
        'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
        'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
        'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽',
        'z': '⠵', ' ': ' ',  # Space for word separation
        '0': '⠼⠚', '1': '⠼⠁', '2': '⠼⠃', '3': '⠼⠉',
        '4': '⠼⠙', '5': '⠼⠑', '6': '⠼⠋', '7': '⠼⠛',
        '8': '⠼⠓', '9': '⠼⠊',
        ',': '⠂', ';': '⠆', ':': '⠒', '.': '⠲',
        '!': '⠖', '?': '⠦', '“': '⠘', '”': '⠘', '\'': '⠄',
        '-': '⠤', '(': '⠦', ')': '⠴'
        # Add other characters and punctuation as needed
    }
    braille_text = ''.join(braille_dict.get(char.lower(), '') for char in text)
    return braille_text

# Gradio app function
def process_video(uploaded_video):
    try:
        # Write the uploaded video to a temporary file
        with open("temp_video.mp4", "wb") as video_file:
            video_file.write(uploaded_video)

        # Process the video file
        transcribed_text = video_to_text("temp_video.mp4")
        summarized_text = summarize_text(transcribed_text)
        braille_script = text_to_braille(summarized_text)

        # Clean up the temporary files
        os.remove("temp_video.mp4")
        os.remove("temp_audio.wav")

        return transcribed_text, summarized_text, braille_script

    except Exception as e:
        traceback.print_exc()  # Print the stack trace to the console
        return str(e), str(e), str(e)  # Return the exception as a string in all outputs

# Create Gradio interface
iface = gr.Interface(
    fn=process_video,
    inputs=gr.components.File(label="Upload Video", type="binary"),
    outputs=[
        gr.components.Textbox(label="Transcribed Text"),
        gr.components.Textbox(label="Summarized Text"),
        gr.components.Textbox(label="Braille Script")
    ],
    title="Video to Braille Converter",
    description="Upload a video to convert its audio to text, summarize it, and then convert to Braille."
)

# Run the app
iface.launch(share=True)

