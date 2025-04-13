from flask import Flask, render_template, request
import math
import speech_recognition as sr
from datetime import datetime
import re

app = Flask(__name__)

# Save to history
def save_to_history(expression, result):
    with open("history.txt", "a") as file:
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"[{time}] {expression} = {result}\n")

# Convert words to digits and math syntax
def convert_expression(expr):
    expr = expr.lower()

    number_words = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
        "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
        "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
        "eighteen": "18", "nineteen": "19", "twenty": "20", "thirty": "30",
        "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70",
        "eighty": "80", "ninety": "90", "hundred": "100"
    }

    # Replace number words
    for word, digit in number_words.items():
        expr = re.sub(rf"\b{word}\b", digit, expr)

    # Replace operators and functions
    expr = expr.replace("plus", "+").replace("minus", "-")
    expr = expr.replace("times", "*").replace("multiplied by", "*")
    expr = expr.replace("divided by", "/").replace("over", "/")
    expr = expr.replace("modulus", "%").replace("mod", "%")
    expr = expr.replace("power", "**").replace("raised to", "**")
    expr = re.sub(r"square root of (\d+)", r"math.sqrt(\1)", expr)
    expr = re.sub(r"log of (\d+)", r"math.log10(\1)", expr)
    expr = re.sub(r"factorial of (\d+)", r"math.factorial(\1)", expr)

    return expr

# Manual evaluation function for safe execution
def manual_eval(expr):
    if expr is None or expr.strip() == "":
        return "Error: Empty expression"
    try:
        # Safely evaluate the expression with math functions
        return eval(expr, {"__builtins__": None}, {"math": math})
    except Exception as e:
        return f"Error: {str(e)}"

# Speech-to-text
def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print("You said:", command)
        return command
    except sr.UnknownValueError:
        return "Sorry, I didn't understand that."
    except sr.RequestError:
        return "Sorry, the speech recognition service is down."

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    expression = ""

    if request.method == "POST":
        expression = request.form["expression"]
    elif request.args.get("voice"):
        expression = listen_for_command()

    if expression:
        converted = convert_expression(expression)
        if converted:
            result = manual_eval(converted)
            save_to_history(expression, result)

    history = []
    try:
        with open("history.txt", "r") as file:
            history = file.readlines()[-5:]  # last 5 entries
    except FileNotFoundError:
        history = []

    return render_template("index.html", result=result, history=history)


if __name__ == "__main__":
    app.run(debug=True)
