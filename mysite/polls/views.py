from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import *

# Create your views here.
class IndexView(generic.ListView):
	template_name = 'polls/index.html'
	context_object_name = 'latest_question_list'

	def get_queryset(self):
		return Question.objects.order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
	model = Question
	template_name = 'polls/detail.html'

class ResultView(generic.DetailView):
	model = Question
	template_name = 'polls/results.html'

def vote(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	try:
		# POST request data is a dictionary.
		selected_choice = question.choice_set.get(pk=request.POST['choice'])
	except (KeyError, Choice.DoesNotExist):
		return render(
			request,
			'polls/detail.html',
			{
				'question': question,
				'error_message': 'You didn\'t select a choice.',
			}
			)
	# You can use else statements with try-except? That's new.
	else:
		selected_choice.votes += 1
		selected_choice.save()
		# When dealing with POST data, always return as 'HttpResponseRedirect'
		# To avoind the case of double submission when the user presses the back button.
		return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))