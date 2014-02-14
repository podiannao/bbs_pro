from django.shortcuts import render,render_to_response, RequestContext

from django.http import HttpResponseRedirect, HttpResponse
from bbs.models import *
from django.contrib import comments 
# Create your views here.
import datetime,time
from django.contrib.auth.decorators import login_required 
from django.contrib import auth


new_comment_dic ={}

def login(request):
	return render_to_response('login.html')

def personal_info(request):
	return render_to_response("personal_info.html", {'login_user':request.user})

def new_article(request):
	bbs_form = new_bbs_form() 
	return render_to_response('new_article.html', {'bbs_form':bbs_form})
def add_new_article(request):
	print request.POST
	web_user_name = web_user.objects.get(user__username=request.user)
	bbs_category,color,bbs_title = request.POST['category'], request.POST['color_type'], request.POST['name']
	
	content = request.POST['content']
	new_bbs_obj = bbs.objects.create(title = bbs_title, color_type= color, category = bbs_category, publish_date=datetime.datetime.now(), author = web_user_name, content = content )
	new_bbs_obj.save()

	return HttpResponse(content)
def upload_pic(request):
    if request.method == 'POST':
	print '========'
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            p = web_user.objects.get(user =  request.user.id)
            p.photo = form.cleaned_data['image']
            p.save()
            return HttpResponse('image upload success')
    return HttpResponse('allowed only via POST')



def account_login(request):
        username = request.POST['user']
        password = request.POST.get('password','')
        user = auth.authenticate(username=username,password=password)
        print user,'====='
	if user is not None: #and user.is_active:
                #correct password and user is marked "active"
                auth.login(request,user)
                return HttpResponseRedirect("/")
        else:
                return render_to_response('login.html',{'err':'Wrong username or password!'})

def index(request):

	return render_to_response('index.html',{'login_user': request.user})

def python_bbs(request):
	bbs_list = bbs.objects.all()
	return render_to_response('blog.html', {'bbs_list': bbs_list,'login_user': request.user},context_instance=RequestContext(request))
	#return render_to_response('blog.html', {'bbs_list': bbs_list})

def add_comment(request):
	print request.POST
	s=request.session
	parent_comment_id = ''
	if not request.user.is_authenticated(): # user not login yet
		print '\033[34;1m-----\033[0m',request.user ,request.user.id
		web_user_name = None 
		comment_user = None
		name,email,msg = request.POST['name'], request.POST['email'], request.POST['message']
	else:
		comment_user = request.user
		msg = request.POST['message']
		email, name = request.user.email, request.user.username
	        web_user_name = web_user.objects.get(user__username=request.user)
                print web_user_name.photo,'\033[34;1m--|||||---\033[0m'
	if request.POST.has_key('comment_id'):parent_comment_id = request.POST['comment_id']  #this comment is a child comment 
	bbs_id = request.POST['bbs_id']
	print new_comment_dic

	if new_comment_dic.has_key(s._session_key):
		time_diff = time.time() - new_comment_dic[ s._session_key ]
		if time_diff >30:
			a=comments.models.Comment.objects.create(content_type_id = 9, object_pk=bbs_id, ip_address= parent_comment_id,user=comment_user, web_user = web_user_name,  site_id=1, user_name=name,user_email=email, comment= msg ,submit_date=datetime.datetime.now())
			a.save()
	                new_comment_dic[s._session_key]  = time.time() #add a new comment mark or renew the time stamp  
		else:
			print "need to send a comment after %s seconds" % time_diff
                        return HttpResponse("need to send a comment after %s seconds" % time_diff)
	else:  #first time submit the comment
		new_comment_dic[s._session_key]  = time.time() #add a new comment mark or renew the time stamp  
		a=comments.models.Comment.objects.create(content_type_id = 9, object_pk=bbs_id, ip_address= parent_comment_id,  site_id=1,user=comment_user, web_user=web_user_name, user_name=name,user_email=email, comment= msg ,submit_date=datetime.datetime.now())
		a.save()

	bbs_obj = bbs.objects.get(id = bbs_id)
	bbs_comments = comments.models.Comment.objects.filter(object_pk= bbs_id)
	return render_to_response('bbs_detail.html', {'bbs_obj':bbs_obj, 'bbs_comments': bbs_comments,'login_user': request.user})

def add_agree(request):
	bbs_id = request.POST['bbs_id']
	bbs_obj = bbs.objects.get(id = bbs_id)
	if request.POST['agree'] == 'YES':
		bbs_obj.agree_count += 1
	else:
		bbs_obj.agree_count -= 1
	bbs_obj.save()
	print bbs_id,'||||'
	return HttpResponse( bbs_obj.agree_count )
def bbs_detail(request):
	print len(request.POST),request.POST
	
	if len(request.POST) != 0:
		bbs_id =  request.POST['BBS_ID'].split('_')[1]
		bbs_obj = bbs.objects.get(id = bbs_id)
		bbs_comments = comments.models.Comment.objects.filter(object_pk= bbs_id)
		print bbs_comments
		bbs_obj.view_count += 1
		bbs_obj.save()
		return render_to_response('bbs_detail.html', {'bbs_obj':bbs_obj, 'bbs_comments': bbs_comments, 'login_user': request.user})
	else:
		bbs_list = bbs.objects.all()
		return render_to_response('blog.html', {'bbs_list': bbs_list})
