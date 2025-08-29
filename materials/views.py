from rest_framework import viewsets
from .models import Course
from .serializers import CourseSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import Lesson
from .serializers import LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer



class LessonListCreateView(generics.GenericAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get(self, request, *args, **kwargs):
        lessons = self.get_queryset()
        serializer = self.get_serializer(lessons, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LessonDetailView(generics.GenericAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_object(self):
        return super().get_object()

    def get(self, request, *args, **kwargs):
        lesson = self.get_object()
        serializer = self.get_serializer(lesson)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        lesson = self.get_object()
        serializer = self.get_serializer(lesson, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        lesson = self.get_object()
        lesson.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)