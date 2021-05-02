from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.template import loader
from django.http import HttpResponse
from core.settings import BASE_DIR
from django.http.response import StreamingHttpResponse
from .camera import VideoCamera, NewFaceData
from .forms import AddPersonsForm
from .models import PersonName, FaceDetectedTime
from authentication.models import UserAlert
from django.contrib import messages
import cv2
import numpy as np
import os 
from PIL import Image


@login_required(login_url="/login/")
def index(request):
    if request.method == "POST":
        Person_add_form = AddPersonsForm(request.POST)
        if Person_add_form.is_valid():
            Person_add_form.save()
            # messages.success(
            #     request, "Your Profile is updated successfully")
            return redirect('new-user-data.html')
    else:
        Person_add_form = AddPersonsForm()
        
    detected_face_list = FaceDetectedTime.objects.order_by('-id')[:5]
    context = {
        'Person_add_form': Person_add_form,
        'detected_face_list': detected_face_list,
    }
    return render(request, 'index.html', context)

@login_required(login_url="/login")
def live_cam(request):
    template = "pages/live-cam.html"
    return render(request,template)

@login_required(login_url="/login")
def face_detected_list(request):
    detected_face_list = FaceDetectedTime.objects.order_by('-id')
    paginator = Paginator(detected_face_list, 20)
    page_number = request.GET.get('page')
    detected_face_list = paginator.get_page(page_number)

    return render(request, 'pages/face-detected-list.html', {'detected_face_list': detected_face_list})
    

# @login_required(login_url="/login")
# def Person_add(request):
#     if request.method == "POST":
#         Person_add_form = AddPersonsForm(request.POST)
#         if Person_add_form.is_valid():
#             Person_add_form.save()
#             # messages.success(
#             #     request, "Your Profile is updated successfully")
#             return redirect('new-user-data.html')
#     else:
#         Person_add_form = AddPersonsForm()
    
#     detected_face_list = FaceDetectedTime.objects.order_by('-id')[:5]
#     alert_email = UserAlert.objects.get(user__username=request.user.username).alert_email
#     alert_email_subject = UserAlert.objects.get(user__username=request.user.username).alert_email_subject
#     alert_email_body = UserAlert.objects.get(user__username=request.user.username).alert_email_body

#     context = {
#         'Person_add_form': Person_add_form,
#         'detected_face_list': detected_face_list,
#         'alert_email': alert_email,
#         'alert_email_subject': alert_email_subject,
#         'alert_email_body': alert_email_body,
#     }

#     return render(request, 'index.html', context)




@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        template = loader.get_template('pages/' + load_template)
        return HttpResponse(template.render(context, request))

    except:

        template = loader.get_template( 'pages/error-404.html' )
        return HttpResponse(template.render(context, request))


# LIVE CAMMERA
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request):
    obj = request.user
    return StreamingHttpResponse(gen(VideoCamera(obj)),
                    content_type='multipart/x-mixed-replace; boundary=frame')


def new_face_data(request):
    return StreamingHttpResponse(gen(NewFaceData()),
                    content_type='multipart/x-mixed-replace; boundary=frame')




#  VIEWS FOR DATASET TRAINING
def train(request):
    url = request.META.get("HTTP_REFERER")
    print(request.user.username)
    path = BASE_DIR+"/app/dataset"

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(BASE_DIR+"/app/haarcascade_frontalface_default.xml")

    def getImagesAndLabels(path):

        imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
        faceSamples=[]
        ids = []

        for imagePath in imagePaths:

            PIL_img = Image.open(imagePath).convert('L') 
            img_numpy = np.array(PIL_img,'uint8')

            id = int(os.path.split(imagePath)[-1].split(".")[1])
            # name = os.path.split(imagePath)[-1].split(".")[1]
            faces = detector.detectMultiScale(img_numpy)

            for (x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                ids.append(id)
                # print (id)
                # names.append(name)
                # print (name)

        return faceSamples,ids
    
    faces,ids = getImagesAndLabels(path)
    # faces,names = getImagesAndLabels(path)
    recognizer.train(faces, np.array(ids))

    recognizer.write(BASE_DIR+'/app/trainer/trainer.yml') 
    messages.success(request, "[INFO] {0} faces trained. All Faces training complete.".format(len(np.unique(ids))))

    return HttpResponseRedirect(url)


"""
#  VIEWS FOR DATASET CREATION
def create_dataset(request):
    url = request.META.get("HTTP_REFERER")

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cam.set(3, 640)
    cam.set(4, 480) 
    face_detector = cv2.CascadeClassifier(BASE_DIR+'/app/haarcascade_frontalface_default.xml')
    count = 0

    while(True):

        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        for (x,y,w,h) in faces:

            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
            count += 1

            # cv2.imwrite("dataset/" + str(face_name) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
            cv2.imwrite(BASE_DIR+"/app/dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
            cv2.putText(img,str(count),(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)

            cv2.imshow('image', img)
        
        k = cv2.waitKey(10) & 0xff 
        if k == 27:
            break
        elif count == 200: 
            break

    cam.release()

    cv2.destroyAllWindows()

    return HttpResponseRedirect(url)


#  VIEWS FOR FACE DETECTION
def detect(request):
    url = request.META.get("HTTP_REFERER")  # get last url

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(BASE_DIR+'/app/trainer/trainer.yml')
    cascadePath = BASE_DIR+"/app/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)
    font = cv2.FONT_HERSHEY_SIMPLEX
    id = 3
    names = ['','Meraj','Imran', 'Rashed'] 

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cam.set(3, 1024)
    cam.set(4, 768)

    while True:
        ret, img =cam.read()
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale( 
            gray,
            scaleFactor = 1.3,
            minNeighbors = 5
           )

        for(x,y,w,h) in faces:

            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
            #confidence = " {0}%".format(round(100 - confidence))
            confidence = int(100*(1 - confidence/300))
            display_conf = str(confidence)+'%'

            if (confidence > 75):
                id = names[id]
            else:
                id = "unknown"
            
            cv2.putText(img, str(id), (x+5,y-5), font, 1, (127,255,212), 2)
            cv2.putText(img, str(display_conf), (x+5,y+h-5), font, 1, (255,255,0), 1)  
        
        cv2.imshow('camera',img) 

        k = cv2.waitKey(10) & 0xff 
        if k == 27:
            break


    print("\n Exit Program!!!")
    cam.release()
    cv2.destroyAllWindows()

    return HttpResponseRedirect(url)
"""