from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q


from .models import Task
from .serializers import TaskSerializer


class IsCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user

class IsCreatorOrMembers(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.creatorr == request.user
            or request.user in obj.members.all()
        )


class TaskListCreateAPIView(ListCreateAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Task.objects.all()
        # return Task.objects.filter(Q(creator=self.request.user) | Q(members=self.request.user)).distinct()
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
    

class TaskDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    lookup_field = "pk"
    permission_classes = [IsAuthenticated, IsCreatorOrMembers]


class TaskDetailAPIView(APIView):
    def get_object(self):
        return get_object_or_404(Task, id=self.kwargs["pk"])
    
    def get(self, request, pk):
        task = self.get_object()
        serializer = TaskSerializer(instance=task)
        return Response(serializer.data)
    
    def put(self, request, pk):
        task = self.get_object()
        serializer = TaskSerializer(
            instance=task,
            data=request.data,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        task = self.get_object()
        serializer = TaskSerializer(
            instance=task,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        task = self.get_object()
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class TaskMarkDoneAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCreator]
    def post(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        self.check_object_permissions(request, task)
        try:
            task.mark_done()
        except DjangoValidationError as e:
            raise DRFValidationError(e.messages)
        serializer = TaskSerializer(instance=task)
        return Response(serializer.data)
    
class TaskReopenAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCreator]
    def post(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        self.check_object_permissions(request, task)
        try:
            task.reopen()
        except DjangoValidationError as e:
            raise DRFValidationError(e.messages)
        serializer = TaskSerializer(instance=task)
        return Response(serializer.data)
    


