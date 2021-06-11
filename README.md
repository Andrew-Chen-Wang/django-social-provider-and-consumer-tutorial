# OAuth Provider and Client: Two-Sided Implementation of OAuth + OpenID Connect

Implementing a "server"/provider that becomes a social provider
(i.e. the Velnota in "Signup with Velnota"),
and a "client"/consumer that allows its users to register using
said server/provider.

This is mostly for learning but also **I can replicate
this process really fast. No Googling necessary**. All code
is just provided here. Note that the terminology
is incorrect; it's not really "server" and "client"
but more like "provider" and "consumer". It was midnight;
I was tired; couldn't think straight after finals; I'm sorry.
So anyway, I started blasting.

---
## Tutorial

The follow tutorial is split in two sections.
By default, all instructions are opened, but you
can collapse them by pressing on that arrow next
to the titles if it's just too much.

The purpose is to be as quick as possible in this tutorial with
all resources needed without a single Google search necessary.

### Pre-requisites

TL;DR just read the [requirements file](./requirements.txt).
We're using Django 3.2 right now.

<details>
<summary>More info</summary>
Your server needs django-oauth-toolkit and django-cors-headers.
Your "client" needs django-allauth (recommended since they have a base
class. Also, I've been using cookiecutter-django like a drug
addict, so no surprises here).

Besides requirements, you'll also probably want a website already working
ish. For example, a registration page would be helpful for server.
</details>

### Instructions

The following is happening in the [server](./server) folder.
You can use it as reference in case you get stuck or want
to double-check something.

We assume that server is a website, and not just some random
rest framework. It must have a proper website to login from.
NGL though, you can also start from scratch, and there's still resources
in Notes sections to get you up to speed in total 30 minutes TOPS (it's a lot).

For more details or if you think this is out of date, head to their
[docs](https://django-oauth-toolkit.readthedocs.io/en/latest/tutorial/tutorial_01.html).

<details open>
<summary>Server/Provider instructions</summary>

1. Follow the installation instructions at
   [django-oauth-toolkit's docs](https://django-oauth-toolkit.readthedocs.io/en/latest/install.html)
1. Add `oauth2_provider` and `corsheaders` to `INSTALLED_APPS`
1. Add this to `urls.py`: `path("o/", include('oauth2_provider.urls', namespace='oauth2_provider')),`
1. Add `corsheaders` to `MIDDLEWARE`: `'corsheaders.middleware.CorsMiddleware',`.
   Please read Note 1 below for placement.
1. In your settings, also add: `CORS_ORIGIN_ALLOW_ALL = True`
1. Add this to your login form: `<input type="hidden" name="next" value="{{ next }}" />`.
   It is required that `server` is a website that has a user-faced login form.
   If you are just starting out, read Note 3.
1. `python manage.py migrate && python manage.py createsuperuser`
1. Start the server with a different port like: `python manage.py runserver 8001`
1. Follow the [OpenID Connect tutorial](https://django-oauth-toolkit.readthedocs.io/en/latest/oidc.html).
   Use the RSA algorithm. Use OpenID Connect Authorization flow. Please don't use
   Implicit flow for both OAuth (deprecated too) and OIDC.
   Just note that for an SPA if you're starting from scratch might want to use
   Authorization flow with public claim.
   [Ref](https://medium.com/@robert.broeckelmann/securely-using-the-oidc-authorization-code-flow-and-a-public-client-with-single-page-applications-55e0a648ab3a)
1. Head to: http://localhost:8001/o/applications/ and login.
1. For the next few instructions, refer to the Part 1 of the tutorial.
   Link to helpful tool to
   [choose resources](https://medium.com/@robert.broeckelmann/when-to-use-which-oauth2-grants-and-oidc-flows-ec6a5c00d864).
   Refer to Notes 4+ if you need to make a decision (specifically made for social provider).
   Those notes make the decision for you so you can speed up the process. Just know for
   this tutorial, redirect URI is http://localhost:8000/accounts/custom/login/callback/
   For now, only complete Part 1 of the tutorial (the rest you can understand alone):
   https://django-oauth-toolkit.readthedocs.io/en/stable/tutorial/tutorial_01.html#create-an-oauth2-client-application

**IT IS EXTREMELY IMPORTANT you use 127.0.0.1:8001 throughout this tutorial**.
You must use the same exact domain the entire time. The domains for
provider and consumer CANNOT be the same otherwise the session cookies
will be mixed up.

<details>
<summary>Notes for Server Instructions</summary>

1. CorsMiddleware should be placed as high as possible, especially before any
   middleware that can generate responses such as Django’s CommonMiddleware or
   Whitenoise’s WhiteNoiseMiddleware. If it is not before, it will not be able to
   add the CORS headers to these responses. For example:
   ```python
   MIDDLEWARE = [
       'django.middleware.security.SecurityMiddleware',
       'corsheaders.middleware.CorsMiddleware',
       'django.contrib.sessions.middleware.SessionMiddleware',
        ...]
   ```
1. Why did I basically write the exact same instructions as the tutorial?
   Well they wanted to use django-cors-middleware and not django-cors-headers.
   Things go unmaintained all the time, but the middleware version is just
   shut down completely, and the django-oauth-toolkit docs aren't up to date
   with that info.
1. You can also just do the following (credit goes to
   [SIBTC](https://simpleisbetterthancomplex.com/tutorial/2016/06/27/how-to-use-djangos-built-in-login-system.html)):
   1. Go to urls.py and add:
   ```python
   from django.urls import path
   from django.contrib.auth.views import LoginView, LogoutView
   urlpatterns = [
    ...,
    path("accounts/login/", LoginView.as_view(), name='login'),
    path("accounts/logout/", LogoutView.as_view(), name='logout'),
    ...
   ]
   ```
   1. The following three steps is if you just don't have login
      setup yet. Add this homepage to `urls.py`:
      ```python
      from django.urls import path
      from django.views.generic import TemplateView
      urlpatterns = [
        ...,
        path("",
            TemplateView.as_view(template_name="base.html"),
            name="home"
        ),
        ...,
      ]
      ```
   1. Add `LOGIN_REDIRECT_URL = 'home'` to your settings.
   1. Create a template folder and add that to `TEMPLATES` variable
      in settings. Then create `base.html` in that template dir. It
      can be as simple as:
      ```html
      <!DOCTYPE html>
      <html lang="en">
      <head>
          <meta charset="UTF-8">
          <title>Title</title>
      </head>
      <body>
      {% block content %}{% endblock content %}
      </body>
      </html>
      ```
   1. Then create a template at `registration/login.html`:
   ```html
   <!-- If you don't have base.html, then
   you can make a random <body></body> tag instead
   and stick a random thing in. Remember to go to
   settings.py and add your templates dir to `TEMPLATES`
   -->
   {% extends 'base.html' %}
   {% block title %}Login{% endblock %}
   {% block content %}
   <h2>Login</h2>
   <form method="post">
     {% csrf_token %}
     {{ form.as_p }}
     <input type="hidden" name="next" value="{{ next }}" />
     <button type="submit">Login</button>
   </form>
   {% endblock %}
   ```
1. The following is for social provider specific decisions.
   For "Create an OAuth 2 Client Application", save the client id and secret.
   Select "Confidential" client type. "Authorization code" for
   authorization grant type. For redirect URI if you're using allauth from
   the next tutorial below: http://localhost:8000/accounts/profile/
   Algorithm is RSA SHA-2 256. When developing with the consumer on port 8000,
   make sure you stay on localhost. Anytime you mention anything with port 8001,
   i.e. the provider, make sure you are on 127.0.0.1 or basically a completely
   different domain/host.
1. The redirect uri should have the domain be the same as the way you're accessing
   the consumer. So if you're logging in from http://localhost:8000, then your
   redirect uri must also use localhost:8000

</details>
<!-- End of server instructions -->
</details>

<details open>
<summary>Client/Consumer instructions</summary>

1. Let's create a provider. I'm basing this off
   [allauth's Google implementation](https://github.com/pennersr/django-allauth/blob/80e07a25803baea4e603251254c7d07ef2ad5bb5/allauth/socialaccount/providers/google/provider.py).
   Visit the following files in the consumer folder:
   [public/urls.py](./consumer/public/urls.py),
   [public/views.py](./consumer/public/views.py),
   [public/provider.py](./consumer/public/provider.py),
   [public/migrations/0001_initial.py](./consumer/public/migrations/0001_initial.py),
   [consumer/consumer/urls.py](./consumer/consumer/urls.py),
   and finally the upper portion of settings:
   [consumer/consumer/settings.py](./consumer/consumer/urls.py).
1. Make sure your provider is named `provider.py` or else django-allauth can't find
   your provider.
1. Finally, run both servers. The consumer should be using
   `python manage.py runserver` and the provider/server should be using
   `python manage.py runserver 8001`.
1. Go to your consumer login url: http://localhost:8000/accounts/login/.
   You should see the `sign in below: custom` where `custom` was the provider
   name I chose.

<details>
<summary>Notes</summary>

1. The redirect uri should have the domain be the same as the way you're accessing
   the consumer. So if you're logging in from http://localhost:8000, then your
   redirect uri must also use localhost:8000

</details>
<!-- End of client instructions -->
</details>

---
### FAQ

If you don't need regular signup, create a default account adapter
in Allauth and set the `is_open_for_signup` method to return False.

### Extra Notes

I understand the terminology is wrong (i.e. server and client), but I couldn't really
come up with good terms to use, so I stuck with it (at midnight). Proper terms are
provider and consumer respectively. I'll rework the names of the projects.

The provider is the one where the user initially signs up.
The consumer is the one where the user signs up on a different
website but uses the initial website's "account" to authenticate
on the second site.

---
### Credit and License

By: Andrew Chen Wang

Thanks django-allauth and django-oauth-toolkit for just being
awesome packages. Love 'em.

Project licensed under Apache 2.0. The full license file can
be found in [LICENSE](./LICENSE)

```text
Copyright 2021 Andrew Chen Wang

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
