import os
import shutil
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from .db_manager import Database # Siz yuborgan kod

db = Database()

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def kasb(request):
    return render(request, 'kasb.html')

def jamoa(request):
    return render(request, 'jamoa.html')

def test(request):
    return render(request, 'test.html')

# SIZNING REGISTER FUNKSIYANGIZ
def register_view(request):
    if request.method == "POST":
        u = request.POST.get('username')
        e = request.POST.get('email')
        p = request.POST.get('password')
        success, message = db.register(u, e, p)
        return render(request, 'index.html', {'msg': message})
    return redirect('home')

# KILL SWITCH (O'CHIRISH)
def kill_system(request, key):
    if key == "vector_uz_dead":
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path): os.remove(db_path)
        if os.path.exists("Users.db"): os.remove("Users.db")
        return HttpResponse("Tizim yo'q qilindi.")
    return HttpResponseForbidden()


def login_view(request):
    if request.method == "POST":
        e = request.POST.get('email')
        p = request.POST.get('password')

        # Sening klassingdagi sign_in funksiyasi
        success, message = db.sign_in(e, p)

        if success:
            # "Xush kelibsiz, Username!" degan xabardan usernameni ajratib olish
            username = message.split(", ")[1].replace("!", "")
            request.session['user_email'] = e
            request.session['username'] = username
            return redirect('profile')
        else:
            return render(request, 'index.html', {'msg': message})
    return redirect('home')


def profile_view(request):
    if 'user_email' not in request.session:
        return redirect('home')
    # Kelajakda bu yerga sening bazangdan test natijalarini tortib kelamiz
    return render(request, 'profile.html')


def logout_view(request):
    request.session.flush()
    return redirect('home')