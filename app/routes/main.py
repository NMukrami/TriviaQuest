import html
import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import random

app = Blueprint('main', __name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        num_questions = request.form.get('num_questions')
        if not num_questions.isdigit() or not (1 <= int(num_questions) <= 50):
            flash("Please enter a valid number between 1 and 50.")
            return redirect(url_for('main.home'))

        session['questions'] = fetch_questions(int(num_questions))
        session['current_question_index'] = 0  # Initialize the question index
        session['user_answers'] = []
        return redirect(url_for('main.question'))

    return render_template('quiz.html')

@app.route('/question', methods=['GET', 'POST'])
def question():
    questions = session.get('questions')
    current_question_index = session.get('current_question_index')

    if questions is None or current_question_index is None or current_question_index >= len(questions):
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        user_answer = request.form.get('answer')
        if user_answer:
            session['user_answers'].append(user_answer)
            session['current_question_index'] += 1  # Increment the index only after saving the answer
            if session['current_question_index'] >= len(questions):
                return redirect(url_for('main.result'))

        return redirect(url_for('main.question'))

    current_question = questions[current_question_index]
    options = current_question['incorrect_answers'] + [current_question['correct_answer']]
    options = list(map(html.unescape, options))
    random.shuffle(options)

    question_number = current_question_index + 1
    total_questions = len(questions)
    print(current_question)
    return render_template('question.html', question=html.unescape(current_question['question']), options=options, question_number=question_number, total_questions=total_questions)

@app.route('/result')
def result():
    questions = session.get('questions')
    user_answers = session.get('user_answers')

    if not questions or not user_answers:
        return redirect(url_for('main.home'))

    score = 0
    for question, user_answer in zip(questions, user_answers):
        correct_answer = html.unescape(question['correct_answer'])
        if user_answer == correct_answer:
            score += 1

    total_questions = len(questions)
    final_score = f"Your Score is: {score}/{total_questions}"

    return render_template('result.html', score=final_score)

def fetch_questions(amount):
    api_url = f"https://opentdb.com/api.php?amount={amount}&category=18&type=multiple"
    response = requests.get(api_url)
    data = response.json()
    questions = data['results']
    for question in questions:
        question['correct_answer'] = html.unescape(question['correct_answer'])
        question['incorrect_answers'] = [html.unescape(ans) for ans in question['incorrect_answers']]
        question['question'] = html.unescape(question['question'])
    return questions

@app.route('/trivia', methods=['GET'])
def get_trivia():
    num_questions = request.args.get('num_questions', default=3)
    api_url = f"https://opentdb.com/api.php?amount={num_questions}&category=18&type=multiple"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({"error": "Failed to fetch trivia questions"}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
