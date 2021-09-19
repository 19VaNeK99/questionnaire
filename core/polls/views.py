from django.shortcuts import render

from .serializers import QuestionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .models import Question
from rest_framework import viewsets


class GetQuestion(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()


