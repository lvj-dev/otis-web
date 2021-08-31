import logging
import traceback
from hashlib import sha256
from typing import Any, Dict

from allauth.socialaccount.models import SocialAccount
from arch.models import Hint, Problem
from core.models import Unit
from dashboard.models import ProblemSuggestion, PSet
from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls.base import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from roster.models import Student, StudentRegistration, UnitInquiry

# Create your views here.


def venueq_handler(action: str, request: HttpRequest) -> JsonResponse:
	if action == 'grade_problem_set':
		# mark problem set as done
		pset = get_object_or_404(PSet, pk=request.POST['pk'])
		pset.approved = bool(request.POST['approved'])
		pset.clubs = request.POST.get('clubs', None)
		pset.hours = request.POST.get('hours', None)
		pset.save()
		# unlock the unit the student asked for
		finished_unit = get_object_or_404(Unit, pk=request.POST['unit__pk'])
		student = get_object_or_404(Student, pk=request.POST['student__pk'])
		if 'next_unit_to_unlock__pk' not in request.POST:
			unlockable_units = student.generate_curriculum_queryset().exclude(has_pset=True).exclude(
				id__in=student.unlocked_units.all()
			)
			target = unlockable_units.first()
		else:
			target = get_object_or_404(Unit, pk=request.POST['next_unit_to_unlock__pk'])
		if target is not None:
			student.unlocked_units.add(target)
		student.unlocked_units.remove(finished_unit)
		return JsonResponse({'result': 'success'}, status=200)
	elif action == 'approve_inquiries':
		for inquiry in UnitInquiry.objects.filter(status="NEW", student__semester__active=True):
			inquiry.run_accept()
		return JsonResponse({'result': 'success'}, status=200)
	elif action == 'mark_suggestion':
		suggestion = ProblemSuggestion.objects.get(pk=request.POST['pk'])
		suggestion.reason = request.POST['reason']
		suggestion.resolved = True
		suggestion.save()
		return JsonResponse({'result': 'success'}, status=200)
	elif action == 'init':
		data: Dict[str, Any] = {
			'_name':
				'Root',
			'_children':
				[
					{
						'_name':
							'Problem sets',
						'_children':
							list(
								PSet.objects.filter(approved=False, student__semester__active=True).values(
									'pk',
									'approved',
									'feedback',
									'special_notes',
									'student__pk',
									'student__user__first_name',
									'student__user__last_name',
									'student__user__email',
									'hours',
									'clubs',
									'eligible',
									'unit__group__name',
									'unit__code',
									'unit__pk',
									'next_unit_to_unlock__group__name',
									'next_unit_to_unlock__code',
									'next_unit_to_unlock__pk',
									'upload__content',
								)
							)
					}, {
						'_name':
							'Inquiries',
						'inquiries':
							list(
								UnitInquiry.objects.filter(status="NEW", student__semester__active=True).values(
									'pk',
									'unit__group__name',
									'unit__code',
									'student__user__first_name',
									'student__user__last_name',
									'explanation',
								)
							),
					}, {
						'_name':
							'Suggestions',
						'_children':
							list(
								ProblemSuggestion.objects.filter(resolved=False).values(
									'pk',
									'created_at',
									'student__user__first_name',
									'student__user__last_name',
									'source',
									'description',
									'statement',
									'solution',
									'comments',
									'acknowledge',
									'weight',
									'unit__group__name',
									'unit__code',
								)
							)
					}
				],
		}
		return JsonResponse(data, status=200)
	else:
		raise Exception("No such command")


def discord_handler(action: str, request: HttpRequest) -> JsonResponse:
	assert action == 'register'
	# check whether social account exists
	uid = int(request.POST['uid'])
	queryset = SocialAccount.objects.filter(uid=uid)
	if not (n := len(queryset)) == 1:
		return JsonResponse({'result': 'nonexistent', 'length': n})

	social = queryset.get()  # get the social account for this; should never 404
	user = social.user
	student = Student.objects.filter(user=user, semester__active=True).first()
	regform = StudentRegistration.objects.filter(
		user=user, container__semester__active=True
	).first()

	if student is not None:
		return JsonResponse(
			{
				'result': 'success',
				'user': social.user.username,
				'name': social.user.get_full_name(),
				'uid': uid,
				'track': student.track,
				'gender': regform.gender if regform is not None else '?',
				'country': regform.country if regform is not None else '???',
				'num_years': Student.objects.filter(user=user).count(),
			}
		)
	elif student is None and regform is not None:
		return JsonResponse({'result': 'pending'})
	else:
		return JsonResponse({'result': 'unregistered'})


def problems_handler(action: str, request: HttpRequest) -> JsonResponse:
	def err(status: int = 400) -> JsonResponse:
		logging.error(traceback.format_exc())
		return JsonResponse({'error': ''.join(traceback.format_exc(limit=1))}, status=status)

	puid = request.POST['puid'].upper()

	if action == 'hints':
		problem = get_object_or_404(Problem, puid=puid)
		response = {
			'hints': [],
			'description': problem.description,
			'url': problem.get_absolute_url(),
			'add_url': reverse_lazy("hint-create", args=(problem.puid, ))
		}
		for hint in Hint.objects.filter(problem=problem):
			response['hints'].append(
				{
					'number': hint.number,
					'keywords': hint.keywords,
					'url': hint.get_absolute_url(),
				}
			)
		return JsonResponse(response)

	if action == 'create':
		try:
			assert 'description' in request.POST
			problem = Problem(description=request.POST['description'], puid=puid)
			problem.save()
		except (Problem.DoesNotExist, Problem.MultipleObjectsReturned):
			return err()
		else:
			return JsonResponse(
				{
					'edit_url': reverse_lazy('problem-update', args=(problem.puid, )),
					'view_url': problem.get_absolute_url(),
				}
			)

	if action == 'add':
		problem = get_object_or_404(Problem, puid=puid)
		try:
			assert 'content' in request.POST
			assert 'keywords' in request.POST
			assert 'number' in request.POST
			hint = Hint(
				problem=problem,
				content=request.POST['content'],
				keywords=request.POST['keywords'],
				number=request.POST['number'],
			)
			hint.save()
		except AssertionError:
			return err()
		else:
			return JsonResponse({'url': hint.get_absolute_url()})

	return JsonResponse({})


@csrf_exempt
@require_POST
def api(request: HttpRequest) -> JsonResponse:
	action = request.POST.get('action', None)
	if action is None:
		raise SuspiciousOperation('You need to provide an action, silly')
	if settings.PRODUCTION:
		token = request.POST.get('token')
		assert token is not None
		if not sha256(token.encode('ascii')).hexdigest() == settings.API_TARGET_HASH:
			return JsonResponse({'error': "☕"}, status=418)

	if action in ('grade_problem_set', 'approve_inquiries', 'mark_suggestion'):
		return venueq_handler(action, request)
	elif action in ('register'):
		return discord_handler(action, request)
	elif action in ('hints', 'create', 'add'):
		return problems_handler(action, request)
	else:
		return JsonResponse({'error': 'No such command'}, status=400)


# vim: fdm=indent
