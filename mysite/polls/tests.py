import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

# Create your tests here.
class QuestionModelTests(TestCase):
	def test_was_published_recently_for_future_question(self):
		time = timezone.now() + datetime.timedelta(days=30)
		future_question = Question(pub_date=time)
		
		self.assertIs(future_question.was_published_recently(), False)
	
	def test_was_published_recently_for_past_question(self):
		past_time = timezone.now() - datetime.timedelta(days=1, seconds=1)
		past_question = Question(pub_date=past_time)
		
		self.assertIs(past_question.was_published_recently(), False)
		
	def test_was_published_recently_for_recent_question(self):
		recent_time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
		recent_question = Question(pub_date=recent_time)
		
		self.assertIs(recent_question.was_published_recently(), True)
		
def create_question(question_text, days):
	time = timezone.now() + datetime.timedelta(days=days)
	return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
	def test_no_questions(self):
		response = self.client.get(reverse('polls:index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'No polls are available.')
		self.assertQuerySetEqual(
			response.context['latest_question_list'], 
			[]
		)

	def test_past_question(self):
		past_question = create_question(
			question_text='Test Question', 
			days=-30
		)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerySetEqual(
			response.context['latest_question_list'],
			[past_question]
		)
	
	def test_future_question(self):
		future_question = create_question(
			question_text='Time Traveller Question',
			days=30
		)
		response = self.client.get(reverse('polls:index'))
		self.assertContains(
			response, 
			'No polls are available.'
		)
		
	def test_past_and_future_question(self):
		question1 = create_question(
			question_text='Past question',
			days=-30
		)
		question2 = create_question(
			question_text='Future question',
			days=30
		)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerySetEqual(
			response.context['latest_question_list'], 
			[question1]
		)
		
	def test_two_past_questions(self):
		question1 = create_question(
			question_text='Past question 1', 
			days=-30
		)
		question2 = create_question(
			question_text='Past question 2', 
			days=-5
		)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerySetEqual(
			response.context['latest_question_list'], 
			[question2, question1]
		)
	
class QuestionDetailViewTests(TestCase):
	def test_future_question(self):
		future_question = create_question(
			question_text='future question', 
			days=5
		)
		url = reverse(
			'polls:detail', 
			args=(future_question.id,)
		)
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)
			
	def test_past_question(self):
		past_question = create_question(
			question_text='past question', 
			days=-5
		)
		url = reverse(
			'polls:detail', 
			args=(past_question.id,)
		)
		response = self.client.get(url)
		self.assertEqual(
			response.status_code, 
			200
		)
		self.assertContains(
			response,
			past_question.question_text
		)
		
		
		