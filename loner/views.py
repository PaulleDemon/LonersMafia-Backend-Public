from django.contrib.auth import login
from django.shortcuts import redirect, render

from user.models import User


# used to login admins
def admin_login(request):

    error = ""
    
    email = request.POST.get("email")
    password = request.POST.get("password")
    if email and password:
        try:
            user = User.objects.get(email=email)

            valid = user.check_password(password)

            if user.is_staff and valid:
                login(request, user)
                return redirect('/admin/')
            
            elif valid:
                return redirect("https://lonersmafia.com")
            

        except (User.DoesNotExist, User.MultipleObjectsReturned) as e:
            pass

        error = "Email and password didn't match"

    return render(request, "admin-index.html", context={"errors": error})