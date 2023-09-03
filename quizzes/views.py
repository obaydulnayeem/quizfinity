from django.shortcuts import render, redirect
from .models import Quiz
from . models import *
from django.db.models import Avg
from django.db.models import Sum
from django.core.validators import MinValueValidator, MaxValueValidator
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.db.models import Count


def quiz_list_new(request):
    category = request.GET.get('category')
    if category:
        quizzes = Quiz.objects.filter(category=category)
    else:
        quizzes = Quiz.objects.all()
    # return render(request, 'quizzes/quiz_list.html', {'quizzes': quizzes})
    
    # categories = Quiz.objects.values('category').annotate(count=Count('category'))
    return render(request, 'quizzes/quiz_list.html', {'quizzes': quizzes})

# def quiz_detail(request, quiz_id):
#     quiz = Quiz.objects.get(pk=quiz_id)
#     questions = quiz.question_set.all()
#     return render(request, 'quizzes/quiz_detail.html', {'quiz': quiz, 'questions': questions})

def quiz_detail(request, quiz_id):
    quiz = Quiz.objects.get(pk=quiz_id)
    questions = quiz.question_set.all()
    feedback = []

    if quiz.time_limit > 0:
        current_time = datetime.now()
        quiz_start_time = current_time
        quiz_end_time = quiz_start_time + timedelta(seconds=quiz.time_limit)
        time_remaining = max(0, (quiz_end_time - current_time).seconds)
    else:
        time_remaining = None

    if request.method == 'POST':
        user_score = 0
        user_answers = []

        for question in questions:
            selected_option_id = request.POST.get(f'question_{question.id}')
            try:
                selected_option = Option.objects.get(pk=selected_option_id)
            except Option.DoesNotExist:
                return HttpResponse("Invalid option selected. Please try again.")

            user_answers.append(UserAnswer(user=request.user, question=question, selected_option=selected_option))

            # Check if the selected option is correct
            is_correct = selected_option.is_correct
            feedback.append((question, selected_option, is_correct))  # Store feedback

            if is_correct:
                user_score += 1

        UserAnswer.objects.bulk_create(user_answers)  # Save user answers to the database

        # Calculate the user's score and create a UserQuizHistory entry
        score_percentage = (user_score / len(questions)) * 100
        user_history = UserQuizHistory.objects.create(user=request.user, quiz=quiz, score=score_percentage)

        # Get the user rating from the POST data, if available
        user_rating = request.POST.get('user_rating')
        if user_rating is not None:
            try:
                user_rating = int(user_rating)
                # Update quiz's average rating based on user's rating
                Rating.objects.create(user=request.user, quiz=quiz, rating=user_rating)
                total_ratings = Rating.objects.filter(quiz=quiz).count()
                total_rating_sum = Rating.objects.filter(quiz=quiz).aggregate(Sum('rating'))['rating__sum'] or 0
                quiz.average_rating = total_rating_sum / total_ratings
                quiz.save()
            except ValueError:
                # Handle invalid user rating (not an integer) gracefully
                return HttpResponse("Invalid user rating. Please provide a valid rating.")

        return render(request, 'quizzes/quiz_result.html', {'quiz': quiz, 'score_percentage': score_percentage, 'feedback': feedback})

    return render(request, 'quizzes/quiz_detail.html', {'quiz': quiz, 'questions': questions, 'time_remaining': time_remaining})




def quiz_result(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to the login page if the user is not logged in

    # Retrieve the user's quiz history
    user_history = UserQuizHistory.objects.filter(user=request.user).order_by('-id').first()

    if user_history:
        return render(request, 'quizzes/quiz_result.html', {'user_history': user_history})
    else:
        return render(request, 'quizzes/quiz_result.html', {'user_history': None})


def user_progress(request):
    user_history = UserQuizHistory.objects.filter(user=request.user)
    return render(request, 'quizzes/user_progress.html', {'user_history': user_history})


def leaderboards(request):
    top_scores = UserQuizHistory.objects.values('user__username', 'quiz__title').annotate(avg_score=Avg('score')).order_by('-avg_score')[:10]
    return render(request, 'quizzes/leaderboards.html', {'top_scores': top_scores})

def category_list(request):
    categories = Quiz.CATEGORY_CHOICES
    return render(request, 'quizzes/category_list.html', {'categories': categories})


# views.py

from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Quiz, Rating

def rate_quiz(request, quiz_id):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if user is not authenticated

    quiz = Quiz.objects.get(pk=quiz_id)

    if request.method == 'POST':
        user_rating = int(request.POST.get('rating'))
        if 1 <= user_rating <= 7:
            rating, created = Rating.objects.get_or_create(user=request.user, quiz=quiz)
            rating.rating = user_rating
            rating.save()
            messages.success(request, f"You rated '{quiz.title}' with {user_rating} stars.")
        else:
            messages.error(request, "Invalid rating. Please select a rating from 1 to 7.")

    # return redirect('quiz_list')
    return render(request, 'quizzes/rate_quiz.html' , {'quiz': quiz})
    
