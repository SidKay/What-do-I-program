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
	"""
	This creates a question object using the 'question_text' arg as its text
	and can also adjust the 'pub_date' attribute using the 'days' argument.
	"""
	time = timezone.now() + datetime.timedelta(days=days)
	return Question.objects.create(question_text=question_text, pub_date=time)
	
def create_choice(question, choice_text):
	"""
	This takes a question and a choice_text as argument
	and creates a choice for the question passed as an argument.
	"""
	return question.choice_set.create(choice_text=choice_text)

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
		create_choice(past_question, 'Choice 1')
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
		create_choice(future_question, 'Choice 1')
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
		create_choice(question1, 'Choice 1')
		
		question2 = create_question(
			question_text='Future question',
			days=30
		)
		create_choice(question2, 'Choice 1')
		
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
		create_choice(question1, 'Choice 1')
		
		question2 = create_question(
			question_text='Past question 2', 
			days=-5
		)
		create_choice(question2, 'Choice 1')
		
		response = self.client.get(reverse('polls:index'))
		self.assertQuerySetEqual(
			response.context['latest_question_list'], 
			[question2, question1]
		)
		
	def test_question_without_choices(self):
		"""
		Questions without choices aren't displayed.
		Creates a question with no choices and the program should ignore it.
		"""
		question = create_question(
			question_text='Test question no choices', 
			days=-5
		)
		response = self.client.get(reverse('polls:index'))
		self.assertContains(
			response, 
			'No polls are available.'
		)
		
	def test_question_with_choices(self):
		"""
		This displays the questions that come with choices.
		"""
		question = create_question(
			question_text='Test question with choices', 
			days=-5
		)
		create_choice(question, 'Choice 1')
		create_choice(question, 'Choice 2')
		response = self.client.get(reverse('polls:index'))
		self.assertQuerySetEqual(
			response.context['latest_question_list'], 
			[question]
		)
		
	def test_questions_with_and_without_choices(self):
		"""
		This checks for the created questions with choices and returns them.
		"""
		question1 = create_question(
			question_text='Question1', 
			days=-15
		)
		create_choice(question1, 'choice1')
		
		question2 = create_question(
			question_text='Question2', 
			days=-10
		)
		create_choice(question2, 'choice2')
		
		question3 = create_question(
			question_text='Question3', 
			days=-5
		)
		
		response = self.client.get(reverse('polls:index'))
		self.assertQuerySetEqual(
			response.context['latest_question_list'], 
			[question2, question1]
		)
	
class QuestionDetailViewTests(TestCase):
	def test_question_without_choices(self):
		question = create_question(
			question_text='Question without choices',
			days=0
		)
		
		url = reverse('polls:detail', args=(question.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)
		
	def test_question_with_choices(self):
		question = create_question(
			question_text='Question with choices', 
			days=0
		)
		create_choice(question, 'Choice 1')
		
		url = reverse('polls:detail', args=(question.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, question.question_text)
		
	def test_future_question(self):
		future_question = create_question(
			question_text='future question', 
			days=5
		)
		create_choice(future_question, 'Choice 1')
		
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
		create_choice(past_question, 'Choice 1')
	
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
		
class QuestionResultViewTests(TestCase):
	def test_show_results_for_question_with_choices(self):
		question = create_question(
			question_text='Question with choices', 
			days=0
		)
		create_choice(question, 'Choice 1')
		
		url = reverse('polls:results', args=(question.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, question.question_text)
		
	def test_show_results_for_question_without_choices(self):
		question = create_question(
			question_text='Question without choices', 
			days=0
		)
		
		url = reverse('polls:results', args=(question.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)
		
	def test_show_results_for_past_question(self):
		past_question = create_question(
			question_text='past question', 
			days=-10
		)
		create_choice(past_question, 'Choice 1')
		
		url = reverse('polls:results', args=(past_question.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, past_question.question_text)
		
	def test_show_results_for_future_question(self):
		future_question = create_question(
			question_text='future question', 
			days=10
		)
		create_choice(future_question, 'Choice 1')
		
		url = reverse('polls:results', args=(future_question.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)
		