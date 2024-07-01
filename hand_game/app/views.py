from django.shortcuts import render,redirect
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.views import APIView
from rest_framework import status
from django.contrib.auth import login,logout
from django.contrib.auth.hashers import make_password,check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
import random
from app.models import *
from app.serializers import UserSerializer,GetUserSerializer
import re
from datetime import datetime
from app.email import *
# Create your views here.
list=['rock','paper','scissor']

def computer_choose():
    chosen = random.choice(list)
    return chosen

def get_winner(user1,user2):
    if user2 == user1:
        return "Tie"
    elif user1 == "rock" and (user2 == "scissor"):
        return "user1"
    elif user1 == "paper" and user2 == "rock":
        return "user1"
    elif user1 == "scissor" and user2 == "paper":
        return "user1"
    else:
        return "user2"
    
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def get_random_otp():
    randomotp = random.randint(0000, 9999)
    return randomotp 

def index(request):
    return render(request,'index.html')

def game_choose(request):
    return render(request,'game_choose.html')

def company_play(request):
    return render(request,'computer_play.html')

def final_play(request,choice):
    return render(request,'final_play.html', context = {"result":"user1","user1_score":1,"user2_score":1,"tie_score":2,"user1_choose":"rock","user2_choose":"paper","move_left":9})

# remaining : create api for register user(fix keys),get user,edit user, manage email for account verification and otp verify, delete user(admin)
# access the created user for game play, dummy player for computer
 
 
class Register_User(APIView):
    @swagger_auto_schema(
        operation_description="Fill in information to register",
        operation_summary="User registration",
        tags=['User'],
        request_body=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['email','password'],
                properties={
                    'email':openapi.Schema(type=openapi.TYPE_STRING,default='string@gmail.com'),
                    'username':openapi.Schema(type=openapi.TYPE_STRING,default="abc"),
                    'password':openapi.Schema(type=openapi.TYPE_STRING,default="Abc@123"),
                    'avatar': openapi.Schema(type=openapi.TYPE_FILE),
                    'role':openapi.Schema(type=openapi.TYPE_STRING,default= "Player"),
                }
            ),
    )
    def post(self,request):
        password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+=!]).{8,}$"
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        try:
            input = request.data
            
            if not re.match(email_regex, input['email']):
                return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST)
            
            if re.match(password_pattern, input['password']):
                password = make_password(input['password'])
                
                if input['role']=='Admin':
                    input['is_superuser']=True
                    input['is_staff']=True
                
                image_data = input.get('avatar')
                if image_data:
                    image_name = image_data.name
                    input['avatar'] = image_name
                else:
                   input['avatar'] = None 
                serializers = UserSerializer(data=input)
                if serializers.is_valid():
                    random_otp=get_random_otp()
                    serializers.save(password=password,otp=random_otp,otp_created_at=datetime.now())
                    sendotp(input['email'],random_otp)
                    return Response({'status':status.HTTP_201_CREATED,'response':'user registered successfully, We have sended you a account verification code on your email'},status=status.HTTP_201_CREATED)
                return Response({'status':status.HTTP_400_BAD_REQUEST,'response':'user can not be created','error':serializers.errors},status=status.HTTP_400_BAD_REQUEST)
            return Response({'status':status.HTTP_400_BAD_REQUEST,'response':'password must contain a capital letter, lower letter, number and a special character'},status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'status':status.HTTP_500_INTERNAL_SERVER_ERROR,'response':e},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Create login funtion

#user2 for computer
#user1 for user

#remaining have to add funtionality for user2 from differnet website, use websocket and also create a model for user.
class game_play(APIView):
    @swagger_auto_schema(
            operation_description="Play to used for main game play, user can choose rock,paper or scissor, to quit pass quit in user choose",
            operation_summary="API for main gameplay",
            tags=['GamePlay'],
            request_body=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=["user_id","template_id"],
                properties={
                    "user_choose": openapi.Schema(type=openapi.TYPE_STRING,description = "user choose"),  
                },
            ),
            manual_parameters=[
                openapi.Parameter('room',openapi.IN_QUERY,type=openapi.TYPE_INTEGER,description="Enter room number")
            ],
        )
    def post(self,request):
        try:
            input_room = request.query_params.get('room')
            user1_choose = str(request.data['user_choose']).lower()

            if user1_choose.lower() == "quit":
                return Response({"status":status.HTTP_202_ACCEPTED,"response":"user exit successfull,you can start the game any time by room number"},status=status.HTTP_202_ACCEPTED)
            
            print(input_room,user1_choose)
            user1_score = 0
            user2_score = 0
            move_left = 10
            room_details = None
            try:
                room_details = room_model.objects.get(room_number = input_room)
                print("room_details",room_details)

            except Exception as e:
                print(str(e))
                return Response({"status":status.HTTP_404_NOT_FOUND,"result":f"Room number {input_room} not exist"})
            
            if room_details:
                user1_score = room_details.user1_score
                user2_score = room_details.user2_score
                move_left = room_details.moves
                print(user1_score,user2_score,move_left)

            if move_left>0:
                if user1_choose and user1_choose in list:
                    user2_choose = str(computer_choose())  
                    winner = get_winner(user1_choose,user2_choose)

                    if not room_details:
                        user1_score = 1 if winner == 'user1' else 0
                        user2_score = 1 if winner == 'user2' else 0
                        tie_score = 1 if winner == "Tie" else 0
                        res = room_model.objects.create(room_number = input_room,user1_score = user1_score,user2_score = user2_score,moves = move_left-1,tie_score = tie_score)
                        res.save()
                        return Response({"status":status.HTTP_200_OK,"response":{"result":winner,"user1_score":user1_score,"user2_score":user2_score,"tie_score":tie_score,"user1_choose":user1_choose,"user2_choose":user2_choose,"move_left":9}},status=status.HTTP_200_OK)
                    
                    else:
                       room_details.user1_score += 1 if winner == 'user1' else 0
                       room_details.user2_score += 1 if winner == 'user2' else 0
                       room_details.tie_score += 1 if winner == "Tie" else 0
                       room_details.moves -= 1
                       room_details.save()
                       return Response({"status":status.HTTP_200_OK,"response":{"result":winner,"user1_score":room_details.user1_score,"user2_score":room_details.user2_score,"tie_score":room_details.tie_score,"user1_choose":user1_choose,"user2_choose":user2_choose,"move_left":room_details.moves}},status=status.HTTP_200_OK)
                    
                else:
                    return Response({"status":status.HTTP_204_NO_CONTENT,"response":{"result":"User Choose should be either rock,paper or scissor"}})
            else:
                return Response({"status":status.HTTP_400_BAD_REQUEST,"response":{"result":"Your out of move, reset game or start a new game","user1_score":room_details.user1_score,"user2_score":room_details.user2_score,"move_left":room_details.moves}},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status":status.HTTP_500_INTERNAL_SERVER_ERROR,"response":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class create_room(APIView):
    @swagger_auto_schema(
        operation_description="Play to used for main game play",
        operation_summary="API for main gameplay",
        tags=['GamePlay']
    )
    def post(self,request):
        try:
            random_number = random.randint(0000,9999)
            res = room_model.objects.create(room_number = random_number)
            res.save()
            return Response({"status":status.HTTP_200_OK,"response":"Room created succesfully","room_number":random_number})
        except Exception as e:
            return Response({"status":status.HTTP_500_INTERNAL_SERVER_ERROR,"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class join_room(APIView):
    @swagger_auto_schema(
        operation_description="Play to used for main game play",
        operation_summary="API for main gameplay",
        tags=['GamePlay'],
        request_body=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=["user_id","template_id"],
                properties={
                    "room_number": openapi.Schema(type=openapi.TYPE_NUMBER,description = "enter room number"),  
                },
            ),
    )
    def post(self,request):
        try:
            input_room_number = int(request.data['room_number'])
            room_details = room_model.objects.get(room_number = input_room_number)
            if room_details:
                return Response({"status":status.HTTP_200_OK,"response":{"user1_score":room_details.user1_score,"user2_score":room_details.user2_score,"tie_score":room_details.tie_score,"move_left":room_details.moves},"room_number":input_room_number})
            else:
                return Response({"status":status.HTTP_404_NOT_FOUND,"response":f"Room Not founded by number {input_room_number}","room_number":input_room_number})
        except Exception as e:
            return Response({"status":status.HTTP_500_INTERNAL_SERVER_ERROR,"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class delete_game(APIView):
    @swagger_auto_schema(
        operation_description="Play to used for main game play",
        operation_summary="API for main gameplay",
        tags=['GamePlay'],
        request_body=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=["user_id","template_id"],
                properties={
                    "room_number": openapi.Schema(type=openapi.TYPE_NUMBER,description = "enter room number"),  
                },
            ),
    )
    def post(self,request):
        try:
            input_room_number = int(request.data['room_number'])
            room_details = room_model.objects.get(room_number = input_room_number)
            if room_details:
                room_details.delete()
                return Response({"status":status.HTTP_200_OK,"response":"Room game delete successfully"},status=status.HTTP_200_OK)
            else:
                return Response({"status":status.HTTP_404_NOT_FOUND,"response":f"Room Not founded by number {input_room_number}","room_number":input_room_number})
        except Exception as e:
            return Response({"status":status.HTTP_500_INTERNAL_SERVER_ERROR,"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class reset_game(APIView):
    @swagger_auto_schema(
        operation_description="Play to used for main game play",
        operation_summary="API for main gameplay",
        tags=['GamePlay'],
        request_body=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=["user_id","template_id"],
                properties={
                    "room_number": openapi.Schema(type=openapi.TYPE_NUMBER,description = "enter room number"),  
                },
            ),
    )
    def post(self,request):
        try:
            input_room_number = int(request.data['room_number'])
            res = room_model.objects.get(room_number = input_room_number)
            if res:
                res.moves= 10
                res.save()
                return Response({"status":status.HTTP_200_OK,"response":"Room reset successfully","room_number":input_room_number})
            else:
                return Response({"status":status.HTTP_404_NOT_FOUND,"response":f"Room Not founded by number {input_room_number}","room_number":input_room_number})
        except Exception as e:
            return Response({"status":status.HTTP_500_INTERNAL_SERVER_ERROR,"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

