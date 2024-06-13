import html
import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import random

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        amount = request.form.get('amount')
        if not amount.isdigit() or not (1 <= int(amount) <= 50):
            flash("Please enter a valid number between 1 and 50.")
            return redirect(url_for('main.home'))

        session['questions'] = get_question(amount)
        session['current_question'] = 0
        session['answers'] = []
        return redirect(url_for('main.question'))

    return render_template('quiz.html')

@main.route('/question', methods=['GET', 'POST'])
def question():
    questions = session.get('questions')
    current_question = session.get('current_question')

    if questions is None or current_question is None or current_question >= len(questions):
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        user_answer = request.form.get('answer')
        if user_answer:
            session['answers'].append(user_answer)
            session['current_question'] += 1

        if session['current_question'] >= len(questions):
            return redirect(url_for('main.result'))

    question = questions[current_question]
    options = question['incorrect_answers'] + [question['correct_answer']]
    options = list(map(html.unescape, options))
    random.shuffle(options)

    return render_template('question.html', question=html.unescape(question['question']), options=options)

@main.route('/result')
def result():
    questions = session.get('questions')
    answers = session.get('answers')

    if not questions or not answers:
        return redirect(url_for('main.home'))

    score = 0
    for question, user_answer in zip(questions, answers):
        if user_answer == html.unescape(question['correct_answer']):
            score += 1

    question_amount = len(questions)
    final_score = f"Your Score is: {score}/{question_amount}"

    return render_template('result.html', score=final_score)

def get_question(amount):
    api_url = requests.get(f"https://opentdb.com/api.php?amount={amount}&category=18&type=multiple")
    response = api_url.json()
    return response['results']
