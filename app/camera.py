from core.settings import BASE_DIR
from django.shortcuts import redirect, render
from django.contrib import messages
import cv2, os, urllib.request
import numpy as np
from .models import PersonName, FaceDetectedTime
from authentication.models import UserAlert
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from twilio.rest import Client
# import datetime
# import time
# import schedule
import winsound
import threading

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(BASE_DIR+'/app/trainer/trainer.yml')
faceCascade = cv2.CascadeClassifier(BASE_DIR+"/app/haarcascade_frontalface_default.xml")
font = cv2.FONT_HERSHEY_SIMPLEX
user_names = list(PersonName.objects.all().values('person_name'))
new_names = ['',]
for i in user_names:
	new_names.append(i['person_name'])
# last_user_id = PersonName.objects.filter().values('id').order_by('-id').first()
last_user_id = len(new_names) - 1
id = len(new_names)
count = 0
faceCount = 0

# def user_data(request):
# 	user_name = request.user.username 
# 	return user_name

class EmailThread(threading.Thread):
	def __init__(self, email):
		self.email = email
		threading.Thread.__init__(self)
	def run (self):
		self.email.send(fail_silently=False) 

class NewFaceData(object):
	user_names = list(PersonName.objects.all().values('person_name'))
	new_names = ['',]
	for i in user_names:
		new_names.append(i['person_name'])
	last_user_id = len(new_names) - 1

	def __init__(self):
		self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
		self.cam.set(3, 1024)
		self.cam.set(4, 768)

	def __del__(self):
		self.cam.release()

	def get_frame(self):
		global count
		while True:
			ret, img = self.cam.read()
			frame_flip = cv2.flip(img,1)
			gray = cv2.cvtColor(frame_flip, cv2.COLOR_BGR2GRAY)
			faces_detected = faceCascade.detectMultiScale(
				gray, 
				scaleFactor=1.3, 
				minNeighbors=5
			)
			for(x,y,w,h) in faces_detected:
				cv2.rectangle(frame_flip, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2)
				cv2.imwrite(BASE_DIR+"/app/dataset/User." + str(self.last_user_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
				cv2.putText(frame_flip, str(count), (20,40), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0),2)
			if count == 99:
				cv2.putText(frame_flip, str("New face is taken,"), (20,80), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,0),2)
				cv2.putText(frame_flip, str("Now go to dashboard & train the new face..."), (20,120), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,0),2)
			if count == 100:
				break
		
			count += 1
			ret, jpeg = cv2.imencode('.jpg', frame_flip)

			return jpeg.tobytes()


class VideoCamera(object):
	def __init__(self,object=None):
		self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
		self.cam.set(3, 1024)
		self.cam.set(4, 768)
		self.alert_email = UserAlert.objects.get(user__username = object.username).alert_email
		self.alert_email_subject = UserAlert.objects.get(user__username = object.username).alert_email_subject
		self.alert_email_body = UserAlert.objects.get(user__username = object.username).alert_email_body
		self.sms_body = UserAlert.objects.get(user__username = object.username).sms_body
		self.sms_mobile_number = UserAlert.objects.get(user__username = object.username).sms_mobile_number
		# self.date = datetime.date.today()
		# self.time = datetime.datetime.now().time()

	def __del__(self):
		self.cam.release()

	def get_frame(self):
		global email_message
		global faceCount
		global client
		while True:
			ret, img = self.cam.read()
			frame_flip = cv2.flip(img,1)
			gray = cv2.cvtColor(frame_flip, cv2.COLOR_BGR2GRAY)
			faces_detected = faceCascade.detectMultiScale(
				gray, 
				scaleFactor=1.3, 
				minNeighbors=5
			)

			for(x,y,w,h) in faces_detected:

				cv2.rectangle(frame_flip, (x,y), (x+w,y+h), (0,255,0), 2)

				id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
				confidence = int(100*(1 - confidence/300))
				display_conf = str(confidence)+'%'

				if (confidence > 75):
					id = new_names[id]
								
				else:
					id = "unknown"
				if (faceCount % 1 == 0 and faceCount > 1):
					face = FaceDetectedTime(detected_face=id)
					face.save()

				# if (faceCount % 3 == 0 and faceCount > 1):
				# 	email = EmailMessage(
				# 		str(id) + ' is detected, ' + str(self.alert_email_subject),
				# 		str(id) + ' is detected, ' + str(self.alert_email_body),
				# 		'merajhossen420@gmail.com',
				# 		[str(self.alert_email)],
				# 	)
				# 	EmailThread(email).start()
				# 	faceCount = 0

				cv2.rectangle(frame_flip, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2)
				cv2.putText(frame_flip, str(id), (x+5,y-5), font, 1, (127,255,212), 2)
				cv2.putText(frame_flip, str(display_conf), (x+5,y+h-5), font, 1, (255,255,0), 1) 
				faceCount += 1
				winsound.PlaySound(BASE_DIR+"/core/static/assets/alert1.wav", winsound.SND_ASYNC) 		
			
			ret, jpeg = cv2.imencode('.jpg', frame_flip)
			return jpeg.tobytes()




'''
class VideoCamera(object):
	def __init__(self):
		self.video = cv2.VideoCapture(0)

	def __del__(self):
		self.video.release()

	def get_frame(self):
		success, image = self.video.read()
		# We are using Motion JPEG, but OpenCV defaults to capture raw images,
		# so we must encode it into JPEG in order to correctly display the
		# video stream.

		frame_flip = cv2.flip(image,1)
		gray = cv2.cvtColor(frame_flip, cv2.COLOR_BGR2GRAY)
		faces_detected = face_detection_videocam.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
		for (x, y, w, h) in faces_detected:
			cv2.rectangle(frame_flip, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2)
			cv2.putText(frame_flip, "Hello World!!!", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
		
		ret, jpeg = cv2.imencode('.jpg', frame_flip)
		return jpeg.tobytes()

'''
