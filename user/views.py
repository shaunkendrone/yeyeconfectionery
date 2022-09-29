from itertools import product
from multiprocessing import context
import random
from turtle import update
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from .models import AuthUser, CCategory, CTypes, Cart, Sales
from .forms import UserRegisterForm
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.template import loader
from django.http import HttpResponse
from asyncio.windows_events import NULL
from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings
import stripe

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView
stripe.api_key = settings.STRIPE_SECRET_KEY



#Create your views here
def index(request):
    return render(request, 'user/index.html',{'title':'index'})

cartnumber=0

def home(request):
    cartnumber=0
    items = CCategory.objects.all().values()
    template = loader.get_template('home.html')
    itemsc = CCategory.objects.all()
    cartitemsq=[]
    for itemc in itemsc:
        try:
            cookie_val=request.COOKIES[str(itemc.id)]
            if(cookie_val!=NULL):
                cartitemsq.append(cookie_val)
        except:
            pass
        finally:
            if request.user.is_authenticated:
                usernow = request.user
                cartitems= Cart.objects.filter(user=usernow.id).count()
                cartnumber = cartitems
            else:
                cartnumber = len(cartitemsq)
    cont = {
    'username': request.POST.get('username'),
    'items': items,
    'cartnumber':cartnumber,
  }
    return HttpResponse(template.render(cont, request))

# register form
def register(request):
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST) or None
        if form.is_valid():
            username = request.POST.get('username')
            email = request.POST.get('email')
            htmly = get_template('user/Email.html')
            d = { 'username': username }
            subject, from_email, to = 'hello', 'from@example.com', email
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            try:
                msg.send()
            except:
                print("error in sending mail")
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form,'title':'reqister here'})

#login form
def Login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            form = login(request,user)
            messages.success(request, f' welcome {username} !!')
            userid = user.id
            items = CCategory.objects.all()
            context={}
            response = redirect('/')
            for item in items:
                try:
                    cookie_val=request.COOKIES[str(item.id)]
                    if(cookie_val!=NULL):
                       qty = cookie_val
                       prodid = item.id
                       useridp = userid
                       itemdb =  Cart.objects.filter(product=item.id,user=userid).values()
                       if not itemdb:
                            cartit= Cart(product_qty=qty, user=useridp, product=prodid)
                            cartit.save()
                       else:
                            update1 = Cart.objects.get(id=item['id'])
                            update1.product_qty = update1.product_qty + int(qty)
                            update1.save()
                       
                   
                       
                       response.delete_cookie(str(item.id))
                except:
                    pass
                finally:
                    pass
            

            return response
        else:
            messages.info(request, f'account does not exit plz sign in')
    form = AuthenticationForm()
    return render(request, 'user/login.html', {'form':form,'title':'log in'})

def cart(request):
    template = loader.get_template('shopping-cart.html')
    items = CCategory.objects.all()
    cartitemsq=[]
    cartnames=[]
    itemprice=[]
    totalprice=[]
    itemid=[]
    images=[]
    tt =0
    if request.user.is_authenticated:
        usernow = request.user
        
        try:
            cartitemdb= Cart.objects.filter(user=usernow.id).values()
            for itemdb in cartitemdb:
                item =  CCategory.objects.get(id=itemdb['product'])

                cartitemsq.append(itemdb['product_qty'])
                cartnames.append(item.name)
                itemprice.append(item.selling_price)
                itemid.append(item.id)
                images.append(item.category_image)
                k=itemdb['product_qty']*int(item.selling_price)
                totalprice.append(k)
                tt+=k
        except:
            pass
        finally:
            pass

    else:
        for item in items:
            try:
                cookie_val=request.COOKIES[str(item.id)]
                if(cookie_val!=NULL):
                    cartitemsq.append(cookie_val)
                    cartnames.append(item.name)
                    itemprice.append(item.selling_price)
                    itemid.append(item.id)
                    images.append(item.category_image)
                    k=int(cookie_val)*int(item.selling_price)
                    totalprice.append(k)
                    tt+=k
            except:
                pass
            finally:
                pass

    cartnumber = len(cartitemsq) 
    mylist = zip(cartnames,cartitemsq,itemprice,totalprice,itemid,images)
    cont1 = {
    'username': request.POST.get('username'),
    'mylist':mylist,
    'tt':tt,
    'cartnumber':cartnumber
    }
    return HttpResponse(template.render(cont1, request))

def checkout(request):
    
    if request.user.is_authenticated:
        usernow = request.user
        template = loader.get_template('checkout.html')
        
        items = CCategory.objects.all()
        cartitemsq=[]
        cartnames=[]
        itemprice=[]
        totalprice=[]
        itemid=[]
        tt =0
        try:
            cartitemdb= Cart.objects.filter(user=usernow.id).values()
            for itemdb in cartitemdb:
                item =  CCategory.objects.get(id=itemdb['product'])

                cartitemsq.append(itemdb['product_qty'])
                cartnames.append(item.name)
                itemprice.append(item.selling_price)
                itemid.append(item.id)
                k=itemdb['product_qty']*int(item.selling_price)
                totalprice.append(k)
                tt+=k
        except:
            pass
        finally:
            pass
        cartnumber = len(cartitemsq) 
        mylist = zip(cartnames,cartitemsq,itemprice,totalprice,itemid)
        cont2 = {
                'username': request.user.username,
                'mylist':mylist,
                'tt':tt,
                'cartnumber':cartnumber,
        }
        return HttpResponse(template.render(cont2, request))
    else:
        return redirect('/register')


def shop(request):
    cartnumber=0
    template = loader.get_template('shop.html')
    items = CCategory.objects.all().values()
    types = CTypes.objects.all().values()
    ctypes = CTypes.objects.all()
    itemsc = CCategory.objects.all()
    cartitemsq=[]
    categorytype=[]

    for itemc in itemsc:
        for type in ctypes:
            if(itemc.types_id==type.id):
                categorytype.append(type.name)
        try:
            cookie_val=request.COOKIES[str(itemc.id)]
            if(cookie_val!=NULL):
                cartitemsq.append(cookie_val)
        except:
            pass
        finally:
            if request.user.is_authenticated:
                usernow = request.user
                cartitems= Cart.objects.filter(user=usernow.id).count()
                cartnumber = cartitems
            else:
                cartnumber = len(cartitemsq)
    mylist = zip(items,categorytype)
    cont3 = {
    'username': request.POST.get('username'),
    'mylist': mylist,
    'items':items,
    'cartnumber':cartnumber,
    'types': types,
    }
    return HttpResponse(template.render(cont3, request))

def details(request):
    template = loader.get_template('shop-details.html')
    cont4 = {
    'username': request.POST.get('username')
  }
    return HttpResponse(template.render(cont4, request))

def about(request):
    template = loader.get_template('about.html')
    ctypes = CTypes.objects.all()
    itemsc = CCategory.objects.all()
    cartitemsq=[]
    categorytype=[]
    for itemc in itemsc:
        for type in ctypes:
            if(itemc.types_id==type.id):
                categorytype.append(type.name)
        try:
            cookie_val=request.COOKIES[str(itemc.id)]
            if(cookie_val!=NULL):
                cartitemsq.append(cookie_val)
        except:
            pass
        finally:
            if request.user.is_authenticated:
                usernow = request.user
                cartitems= Cart.objects.filter(user=usernow.id).count()
                cartnumber = cartitems
            else:
                cartnumber = len(cartitemsq)
    cont5 = {
    'username': request.POST.get('username'),
    'cartnumber':cartnumber
  }
    return HttpResponse(template.render(cont5, request))

def contact(request):
    template = loader.get_template('contact.html')
    ctypes = CTypes.objects.all()
    itemsc = CCategory.objects.all()
    cartitemsq=[]
    categorytype=[]
    for itemc in itemsc:
        for type in ctypes:
            if(itemc.types_id==type.id):
                categorytype.append(type.name)
        try:
            cookie_val=request.COOKIES[str(itemc.id)]
            if(cookie_val!=NULL):
                cartitemsq.append(cookie_val)
        except:
            pass
        finally:
            if request.user.is_authenticated:
                usernow = request.user
                cartitems= Cart.objects.filter(user=usernow.id).count()
                cartnumber = cartitems
            else:
                cartnumber = len(cartitemsq)
    cont6 = {
    'username': request.POST.get('username'),
    'cartnumber':cartnumber
  }
    return HttpResponse(template.render(cont6, request))

def ToCart(request):
    productid = request.POST['productid']
    if request.user.is_authenticated:
        template = loader.get_template('shopping-cart.html')
        usernow = request.user
        try:
            item =  Cart.objects.get(product=productid,user=usernow.id)
            item.product_qty = item.product_qty+1
            item.save()
        except:
            qty = 1
            prodid = productid
            useridp = usernow.id
            cartit = Cart(product_qty=qty, user=useridp, product = prodid)
            cartit.save()
        cartitems= Cart.objects.filter(user=usernow.id).count()
        cartnumber = cartitems
        context={'cartnumber':cartnumber}
        return redirect(request.META.get('HTTP_REFERER'))
        # return HttpResponse(template.render(context, request))
    else:

        itemsc = CCategory.objects.all()
        cartitemsq=[]
        for itemc in itemsc:
            try:
                cookie_val=request.COOKIES[str(itemc.id)]
                if(cookie_val!=NULL):
                    cartitemsq.append(cookie_val)
            except:
                pass
            finally:
                cartnumber = len(cartitemsq)
        
        
        value=1
        try:
            cookie_val=request.COOKIES[productid]
            if(request.COOKIES[productid]!=NULL):
                value += int(cookie_val)
        except:
            value=1
        finally:
            context={
                'cartnumber':cartnumber

            }

            response = redirect(request.META.get('HTTP_REFERER'))
            response.set_cookie(productid,value,max_age=10800)
  
        return response


def FromCart(request):
    value = request.POST['productvalue']
    productid = request.POST['productid']
        
    if request.user.is_authenticated:
        template = loader.get_template('shopping-cart.html')
        usernow = request.user
        item =  Cart.objects.get(product=productid,user=usernow.id)
        item.product_qty = item.product_qty-1
        if(item.product_qty==0):
            item.delete()
        else:
            item.save()
        cartitems= Cart.objects.filter(user=usernow.id).count()
        cartnumber = cartitems
        context={'cartnumber':cartnumber}
        return redirect(request.META.get('HTTP_REFERER'))
        # return HttpResponse(template.render(context, request))
    else:
        value1=0
        try:
            cookie_val=request.COOKIES[productid]
            if(request.COOKIES[productid]!=NULL):
                value1 = int(value)-1
        except:
            pass
        finally:
            itemsc = CCategory.objects.all()
            cartitemsq=[]
            for itemc in itemsc:
                try:
                    cookie_val=request.COOKIES[str(itemc.id)]
                    if(cookie_val!=NULL):
                        cartitemsq.append(cookie_val)
                except:
                    pass
                finally:
                    cartnumber = len(cartitemsq)
            context={
                'cartnumber':cartnumber
            }

            response = redirect(request.META.get('HTTP_REFERER'))
            response.set_cookie(productid,value1,max_age=10800)

            if(value1<1):
                response.delete_cookie(str(productid))
        
        return response

def remove(request):
   cartname = request.POST['productname']
   productid = request.POST['productid']
   if request.user.is_authenticated:
        template = loader.get_template('shopping-cart.html')
        usernow = request.user
        itemremove =  Cart.objects.get(product=productid,user=usernow.id)
        itemremove.delete()
        cartitems= Cart.objects.filter(user=usernow.id).count()
        cartnumber = cartitems
        context={'cartnumber':cartnumber}
        return redirect(request.META.get('HTTP_REFERER'))
   else:

        items = CCategory.objects.get(name=cartname)
        response = redirect(request.META.get('HTTP_REFERER'))
        response.delete_cookie(str(items.id))
        return response


def shopview(request, id):
    if(CTypes.objects.get(id=id)):
        items = CCategory.objects.filter(types_id=id)
        # types = CTypes.objects.filter(id=id).first()
        types = CTypes.objects.all().values()
        itemsc = CCategory.objects.all()
        cartitemsq=[]
        for itemc in itemsc:
            try:
                cookie_val=request.COOKIES[str(itemc.id)]
                if(cookie_val!=NULL):
                    cartitemsq.append(cookie_val)
            except:
                pass
            finally:
                cartnumber = len(cartitemsq)
        context = {
            'items' :items, 'types' :types, 'cartnumber':cartnumber
        }
        return render(request, "shop.html",context)
    else:
        messages.warning(request, "No such category found")
        return redirect('shop')

def shopdetails(request,id):
    items = CCategory.objects.get(id=id)
    itemtypes = CCategory.objects.filter(types_id=items.types_id)
    template = loader.get_template('shop-details.html')
    itemsc = CCategory.objects.all()
    cartitemsq=[]
    categoryname=CTypes.objects.get(id=items.types_id)
    for itemc in itemsc:
        try:
            cookie_val=request.COOKIES[str(itemc.id)]
            if(cookie_val!=NULL):
                cartitemsq.append(cookie_val)
        except:
            pass
        finally:
            if request.user.is_authenticated:
                usernow = request.user
                cartitems= Cart.objects.filter(user=usernow.id).count()
                cartnumber = cartitems
            else:
                cartnumber = len(cartitemsq)
    context = {
        'categoryname' : categoryname,
    'item' :items, 'cartnumber':cartnumber, 'itemtypes':itemtypes}
    return HttpResponse(template.render(context, request))

def sales(request):
    usernow = request.user
    userid = usernow.id
    tt = request.POST['total']
    address = request.POST['address']
    phone =request.POST['phone']
    name = request.POST['fname']+" "+request.POST['lname']
    cartitems= Cart.objects.filter(user=userid).values()
    paymentmethod = request.POST['paymentmethod']
    ordernumber = random.randint(1000,100000)
    if(paymentmethod == 'cash'):
        for cartitem in cartitems:
            item =  CCategory.objects.get(id=cartitem['product'])
            productid = cartitem['product']
            qty = cartitem['product_qty']
            tot = int(qty)*item.selling_price
            sale = Sales(product_qty=qty, user=userid, product = productid,phone=phone,address=address,total_price=tot,ordernumber=ordernumber,paymentmethod=paymentmethod,name=name)
            sale.save()
            previtem=Cart.objects.get(product=productid,user=userid)
            previtem.delete()
        
        name = name
        email = usernow.email
        content = "Your order has been confirmed. Order number is " + str(ordernumber) + " at a total of UGX "+tt + " to be paid on delivery"
       
           
        html = render_to_string('contactform.html', {
                'name':name,
                'email':email,
                'content':content
            })
        send_mail('The contact form subject', 'This is the message', 'gilbertahabwe5@gmail.com', {email}, html_message=html)

        return render(request, 'ordermade.html',{
            'ordernumber':ordernumber,
            'email':email
        })

    else:
        response = redirect('/home2')
        response.set_cookie('nameyeye',name,max_age=600)
        response.set_cookie('addressyeye',address,max_age=600)
        response.set_cookie('phoneyeye',phone,max_age=600)
        response.set_cookie('totalyeye',tt,max_age=600)
        
        return response

class HomePageView(TemplateView):
    template_name = 'home2.html'

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['key']=settings.STRIPE_PUBLISHABLE_KEY
        return context

def charge(request):
    if request.method == 'POST':
        tt = request.COOKIES['totalyeye']
        charge = stripe.Charge.create(
            amount = 10000000,
            currency = 'UGX',
            description = 'Payment Gateway',
            source = request.POST['stripeToken']
        )

        usernow = request.user
        userid = usernow.id
        address = request.COOKIES['addressyeye']
        phone =request.COOKIES['phoneyeye']
        name = request.COOKIES['nameyeye']
        tt = request.COOKIES['totalyeye']
        cartitems= Cart.objects.filter(user=userid).values()
        paymentmethod = 'credit'
        ordernumber = random.randint(1000,100000)
        for cartitem in cartitems:
                item =  CCategory.objects.get(id=cartitem['product'])
                productid = cartitem['product']
                qty = cartitem['product_qty']
                tot = int(qty)*item.selling_price
                sale = Sales(product_qty=qty, user=userid, product = productid,phone=phone,address=address,total_price=tot,ordernumber=ordernumber,paymentmethod=paymentmethod,name=name)
                sale.save()
                previtem=Cart.objects.get(product=productid,user=userid)
                previtem.delete()

        name = name
        email = usernow.email
        content = "Your order has been confirmed. Order number is " + str(ordernumber) + " at a total of UGX "+tt + " paid using your credit card will be delivered"
       
           
        html = render_to_string('contactform.html', {
                'name':name,
                'email':email,
                'content':content
            })
        send_mail('The contact form subject', 'This is the message', 'gilbertahabwe5@gmail.com', {email}, html_message=html)

    return render(request, 'ordermade.html',{
            'ordernumber':ordernumber,
            'email':email
        })