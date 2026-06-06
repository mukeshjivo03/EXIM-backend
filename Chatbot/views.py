from django.shortcuts import render
from .services import ChatAgent
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ChatView(APIView):

    def post(self , request):
        user_message = request.data.get("message")
        if not user_message:
            return Response({"error" : "User messgae is mandatory"} , status=status.HTTP_400_BAD_REQUEST)
        
        agent = ChatAgent()
        response_text = agent.execute_user_query(user_message)
        
        return Response({"response": response_text}, status=status.HTTP_200_OK)
        