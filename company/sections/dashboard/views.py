from django.shortcuts import render
import requests
from django.contrib.auth import get_user_model

# Use this to get the user model
User = get_user_model()
# Create your views here.

def home(request):

    try:
        # api_url = 'https://api.api-ninjas.com/v1/quotes'
        # response = requests.get(api_url, headers={'X-Api-Key': 'D9hwiVgAtJ4kzEldbMf8jQ==5sC9ziBVgE1Z47mC'})
        # if response.status_code == requests.codes.ok:
        #     result = response.json()
        #     quote = result[0]['quote']
        #     author = result[0]['author']
        pass
    except:
        # print("Error:", response.status_code, response.text)
        pass
  
    
    context = {
        # 'quote': quote,
        # 'author': author,
    }

    return render(request, 'dashboard/home.html', context)