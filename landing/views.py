from django.shortcuts import render
from django.contrib.auth.models import AnonymousUser
from social_django.models import UserSocialAuth
from requests.exceptions import HTTPError
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect

import requests
# import vk


def main_page(request):
    template = 'landing/main_page.html'
    friends = list()

    user_is_anonym = isinstance(request.user, AnonymousUser)
    if user_is_anonym:
        # is anonymous
        name = 'Гость'
    else:
        # is authenticated
        try:
            current_social_user_data = UserSocialAuth.objects.values('extra_data').get(id=request.user.id)
        except UserSocialAuth.DoesNotExist:
            name = 'Гость'
            user_is_anonym = True
        else:
            name = request.user.first_name
            access_token = current_social_user_data['extra_data']['access_token']
            url = f'https://api.vk.com/method/friends.get?order=random&count=5&fields=photo_50&access_token={access_token}&v=5.103'

            try:
                response = requests.get(url)

                response.raise_for_status()
            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
            except Exception as err:
                print(f'Other error occurred: {err}')
            else:
                # print('Success!')
                data_json = response.json()
                if 'error' not in data_json:
                    for num, user_from_request in enumerate(data_json['response']['items'], start=1):
                        user_from_request['num'] = num
                        friends.append(user_from_request)
                else:
                    # на сайте мы ещё залогинены а в вк нет.
                    # Или случилась ещё какая ошибка (error в data_json) Значит
                    # нужно выйти с сайта или заново залогиниться в вк...
                    # будем выходить
                    return redirect('landing:logouut_page')

    context = {
        'user_is_anonym': user_is_anonym,
        'name': name,
        'friends': friends,
        }
    return render(request, template, context=context)


class LogoutView(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy('landing:home')
