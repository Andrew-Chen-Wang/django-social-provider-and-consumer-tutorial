# OAuth Server and Client: Two-Sided Implementation of OAuth + OpenID Connect

Implementing a "server" that becomes a social provider
(i.e. the Velnota in "Signup with Velnota"),
and a client that allows its users to register using
said server.

This is mostly for learning but also, so I can replicate
this process really fast. No Googling necessary. All code
is just provided here.

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

We assume that server is a website, and not just some random
rest framework. It must have a proper website to login from.
NGL though, you can also start from scratch, and there's still
resources to get you up to speed in like 30 minutes TOPS (it's a lot).

For more details or if you think this is out of date, head to their
[docs](https://django-oauth-toolkit.readthedocs.io/en/latest/tutorial/tutorial_01.html).

<details open>
<summary>Server instructions</summary>

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
1. Head to: http://localhost:8001/o/applications/ and login.
1. For the next few instructions, refer to the docs but also COME BACK.
   If you need to, refer to Notes 4+ if you need to make a decision.
   Those notes make the decision for you so you can speed up the process:
   https://django-oauth-toolkit.readthedocs.io/en/1.5.0/tutorial/tutorial_01.html#create-an-oauth2-client-application
   however you should note that I've linked to a specific version to make sure
   there is no link breaking for far in the future usage.
   Test out the `latest` doc page; if it works, then use that instead.
1. Are you back? Great. We need to set up OpenID connect. It's a standardized
   way we can give information to registered social providing clients.
   Basically, follow their OIDC tutorial and use RSA:
   https://django-oauth-toolkit.readthedocs.io/en/stable/oidc.html
   To complement, the client tutorial, we're going to add some fields
   to our current user to make this tutorial more valuable.

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
1. Choose RS256 when registering. It allows for people to
   verify via public key.

</details>
<!-- End of server instructions -->
</details>

<details open>
<summary>Client instruction</summary>

1. Set up django-allauth
1. Let's create a provider. I'm basing this off
   [allauth's Google implementation](https://github.com/pennersr/django-allauth/blob/80e07a25803baea4e603251254c7d07ef2ad5bb5/allauth/socialaccount/providers/google/provider.py).
   In some random but dedicated file:
   ```python
   from allauth.account.models import EmailAddress
   from allauth.socialaccount.app_settings import QUERY_EMAIL
   from allauth.socialaccount.providers.base import AuthAction, ProviderAccount
   from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

   class Scope:
      EMAIL = "email"
      PROFILE = "profile"

   class GoogleAccount(ProviderAccount):
       def get_profile_url(self):
           return self.account.extra_data.get("link")

       def get_avatar_url(self):
           return self.account.extra_data.get("picture")

       def to_str(self):
           dflt = super(GoogleAccount, self).to_str()
           return self.account.extra_data.get("name", dflt)


   class GoogleProvider(OAuth2Provider):
       id = "google"
       name = "Google"
       account_class = GoogleAccount

       def get_default_scope(self):
           scope = [Scope.PROFILE]
           if QUERY_EMAIL:
               scope.append(Scope.EMAIL)
           return scope

       def get_auth_params(self, request, action):
           ret = super(GoogleProvider, self).get_auth_params(request, action)
           if action == AuthAction.REAUTHENTICATE:
               ret["prompt"] = "select_account consent"
           return ret

       def extract_uid(self, data):
           return str(data["id"])

       def extract_common_fields(self, data):
           return dict(
               email=data.get("email"),
               last_name=data.get("family_name"),
               first_name=data.get("given_name"),
           )

       def extract_email_addresses(self, data):
           ret = []
           email = data.get("email")
           if email and data.get("verified_email"):
               ret.append(EmailAddress(email=email, verified=True, primary=True))
           return ret

   provider_classes = [GoogleProvider]
   ```
1. In `INSTALLED_APPS`, add the dotted path to that file.
   This must come after `allauth.socialaccount`

<details>
<summary>Notes</summary>

1.

</details>
<!-- End of client instructions -->
</details>

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