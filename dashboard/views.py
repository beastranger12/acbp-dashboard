from django.conf import settings
from django.shortcuts import render,redirect
import pandas as pd
import numpy as np
import xlsxwriter 
try:
    from io import BytesIO as IO # for modern python
except ImportError:
    from io import StringIO as IO # for legacy python
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from .models import *
from django.db.models import Avg, Count, Min, Sum
from datetime import date, datetime, timedelta, time
import calendar
from django.db import IntegrityError
from django.db import DatabaseError
import traceback

PRODUCT_TYPE = ['homehvac','majorhomeappliances','powertools','inkandtoner','outdoorpower','personalcomputers', 'poolsandspa','kitchenappliances','vacuum', 'grill','camera']
MARKETPLACE = ['1-(US)','3-(UK)','4-(DE)','5-(FR)','6-(JP)','7-(CA)','35691-(IT)','44551-(ES)','111172-(AU)','771770-(MX)','526970-(BR)']
col1=''
col2=''
col3=''
col4=''
col5=''
col6=''
col7=''
col8=''
col9=''

# Create your views here.
def welcome_page(request):
    return render(request,'smt_smpo_dashboard/welcome.html',{})
def current_phase():
    month = datetime.strftime(datetime.today(),"%b")
    batman = str(month)+str(datetime.today().year)
    return batman

def create_phase():
    Month = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    PHASE = []
    today_year = datetime.today().year
    for i in range(len(Month)):
        PHASE.append(str(Month[i])+str(today_year))
    return PHASE

def f(month, year):
  m=list(range(12, 0, -1))*3
  y=[year]*12+[year-1]*12
  return m[13-month:(13-month+12)], y[13-month:(13-month+12)]

def create_phase2():
    Month = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    month_num=['01','02','03','04','05','06','07','08','09','10','11','12']
    PHASE = []
    phase2=[]
    j=1
    today_year = datetime.today().year
    today_month=datetime.today().month
    PHASE.append({'d':str(Month[today_month-1])+str(today_year),'v':str(month_num[today_month-1])+'-'+str(today_year)})
    #phase2.append({'v':str(today_month)+'-'+str(today_year),'d':)
    #print(today_year)
    b=f(today_month, today_year)
    #print(len(b[0])) append({'h':q,'v':0})
    for i in range(len(b[0])):
        m=b[0][i]
        y=b[1][i]
        PHASE.append({'d':str(Month[m-1])+str(y),'v':str(month_num[m-1])+'-'+str(y)})
        #phase2.append()
    return PHASE

def user_login(request):
    template = 'smt_smpo_dashboard/login_form.html'
    if request.POST:
        username=str(request.POST.get('username'))
        password =str(request.POST.get('password'))
        
        user = authenticate(username=username, password=password)

        print(user)

        if user is not None:
            if user.is_active:
                date_today = datetime.today().strftime('%Y-%m-%d')
                check_loggedin = productivity.objects.all().filter(brand="Login",user=username,timestamp__contains=date_today)
                #check whether user logged in today or not
                #check_loggedin=''
                if check_loggedin:
                    login(request, user)
                    if username in get_manager():
                        return redirect('manager')
                    elif username in get_auditor():
                        return redirect('auditor')
                    elif username in get_rda():
                        print(username)
                        return redirect('sme')
                #if user has not logged in today
                else:
                    if str(request.POST.get('login_status')) == 'Work from Office':
                            status = check_login()
                            if status == "NightOWL":
                                print("Do Nothing")
                            elif status == "Half Day":
                                login_log = productivity.objects.create(brand="Login",user=username,sub_task=status,timestamp=datetime.now(),productivity=int(240))
                                login_log.save()
                            else:
                                login_log = productivity.objects.create(brand="Login",user=username,sub_task=status,timestamp=datetime.now(),productivity=int(480))
                                login_log.save()
                    elif str(request.POST.get('login_status')) == 'Work from Home':
                        login_log = productivity.objects.create(brand="Login",user=username,sub_task=str(request.POST.get('login_status')),timestamp=datetime.now(),productivity=int(480))
                        login_log.save()
                    elif str(request.POST.get('login_status')) == 'Half Day':
                        login_log = productivity.objects.create(brand="Login",user=username,sub_task=str(request.POST.get('login_status')),timestamp=datetime.now(),productivity=int(240))
                        login_log.save()
                    #Holiday
                    else:
                        login_log = productivity.objects.create(brand="Login",user=username,sub_task=str(request.POST.get('login_status')),timestamp=datetime.now(),productivity=int(0))
                        login_log.save()

                    login(request, user)
                    if username in get_manager():
                        return redirect('manager')
                    elif username in get_auditor():
                        return redirect('auditor')
                    elif username in get_rda():
                        print(username)
                        return redirect('sme')
                    elif username in get_master():
                        print(username)
                        print('hi')
                        return redirect('master')
                    else:
                        return HttpResponse("<h1>You are not an authorized person! Please contact manager for access.</h1>")
        else:
            return HttpResponse("<h1>"+str(username)+"</h1>")
    return render(request,template,{})
def members_view(request):
    #mngr = ['vishshan','vignev','murugvig']
    mngr=[]
    mngr_ob=profile.objects.all().filter(user_role='manager')
    for i in mngr_ob:
        mngr.append(i.user_name)
    usr = []
    ob = profile.objects.all().exclude(user_role="manager")
    for i in ob:
        usr.append(i.user_name)

    #master_list = []
    #k=0
    #while k!=len(usr):
        # u=[]
        # for i in range(1,5):
        #   u.append(usr[k])
        #     k+=1
        #master_list.append(usr[k])
    return render(request,'smt_smpo_dashboard/members.html',{'mngr':mngr,'usr':usr})
def get_rda():
    obj = profile.objects.all().filter(user_role='rda')|profile.objects.all().filter(user_role='reviewer')|profile.objects.all().filter(user_role='SME')
    rda_list = []
    for rda in obj:
        rda_list.append(rda.user_name)
    rda_list.sort()
    return rda_list
def get_auditor():
    obj = profile.objects.all().filter(user_role='auditor')
    auditor_list = []
    for audt in obj:
        auditor_list.append(audt.user_name)
    auditor_list.sort()
    return auditor_list

def get_manager():
    obj = profile.objects.all().filter(user_role='manager')
    auditor_list = []
    for audt in obj:
        auditor_list.append(audt.user_name)
    auditor_list.sort()
    return auditor_list

def get_master():
    obj = profile.objects.all().filter(user_role='master')
    master_list = []
    for audt in obj:
        master_list.append(audt.user_name)
    master_list.sort()
    return master_list

def get_reviewer():
    reviewer = []
    ob = profile.objects.all().filter(user_role='reviewer')
    for i in ob:
        reviewer.append(i.user_name)
    return reviewer

def get_status():
    ob = benchmark.objects.all().exclude(task__icontains='easible')
    status = []
    for i in ob:
        status.append(i.subtask)
    status.append('Feasibility')
    status.append('Crawl config YTS')
    status.append('Complexity Hours')
    status.sort()
    return status


def get_role(user):
    ob = profile.objects.get(user_name=user)
    return ob.user_role

def get_sp_role1(user):
    ob = profile.objects.get(user_name=user)
    return ob.special_role1

def get_sp_role2(user):
    ob = profile.objects.get(user_name=user)
    return ob.special_role2

def log_rda(request):

	return render(request,'smt_smpo_dashboard/rda.html',{'user':'h','summary':'o','tot':'tot','role':'rda'})

def logout_view(request):
    d = dict()
    d["status"] = "You have been logged out."
    logout(request)
    return render(request, 'smt_smpo_dashboard/logout.html', d)

def check_login():
    if datetime.now().time() >= time(6,0) and datetime.now().time() <= time(10,30):
        return "Work from Office"
    elif datetime.now().time() >= time(10,31) and datetime.now().time() <= time(12,0):
        return "Late Login"
    elif datetime.now().time() >= time(17,0) and datetime.now().time() <= time(5,59):
        return "NightOWL"   
    else:
        return "Half Day" 

def adhoc_form(request):
    current_user = request.user
    user = current_user.username

    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    print(ob)
    if not ob:

        return redirect('login')
        #print('hi')
    else:
        adh_obj = productivity.objects.all().filter(brand="Adhoc",user=user)

        owner = []
        rol = profile.objects.all().filter(user_role='manager')
        for i in rol:
            owner.append(i.user_name)
        
        if request.POST:
            ob = productivity.objects.create(brand="Adhoc",user=user,timestamp= datetime.today(),task=str(request.POST.get('Activity')),sub_task=str(request.POST.get('AdditionalInfo')),website=str(request.POST.get('Adhoc Hours')),brand_iteration=str(request.POST.get('Owner')),phase=current_phase())
            ob.save()

            context = {'user':user,'owner':owner,'user': user,'adh_obj':adh_obj,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
            return render(request,'smt_smpo_dashboard/adhoc_form.html',context)

        context = {'user':user,'owner':owner,'user': user,'adh_obj':adh_obj,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}   
        return render(request,'smt_smpo_dashboard/adhoc_form.html',context)


def current_phase():
    month = datetime.strftime(datetime.today(),"%b")
    phase = str(month)+str(datetime.today().year)
    return phase
def manager(request):
    current_user = request.user
    user= current_user.username

    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    if not ob:
        return redirect('login')
    else:
        
        date_range = []
        delta = timedelta(days=1)

        start_date=datetime.today()
        start_date = start_date.replace(month=1)
        end_date=datetime.today().month
        print(start_date.month)
        print(end_date)
        #print(start_date.strftime("%Y-%m"))
        m=2
        m2=1

        while m2 <= end_date:
            print(start_date.month)
            date_range.append(start_date.strftime("%Y-%m")) 
            if(m<=12):  
                start_date=start_date.replace(month=m)
            #print(start_date)
                m+=1
            m2+=1
        #print(date_range)
        master_list,total = create_homepage_cost('ALL',date_range)
        master_list2=[]
        for l in master_list:
            #print([l[17:]])
            master_list2.append(l[2:])

        context = {'role':get_role(user),'sp_role2':get_sp_role2(user),'user':user,'summary':'summary','tot':'tot','master_list':master_list2}
        return render(request,'smt_smpo_dashboard/manager_homepage.html',context)

def master(request):
    current_user = request.user
    user= current_user.username

    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    if not ob:
        return redirect('login')
    elif not(role_ob.special_role2 == "master"): 
    	return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        if request.POST:
            #print('hi')
            a = brand_program.objects.all()
            mp_id_chk=['4','5','35691', '44551', '6']
            for prog in a:
                prog_brand=str(prog.brand)
                prog_website=str(prog.website)
                prog_website_id=str(prog.website_id)
                prog_language=str(prog.language)
                prog_bus_request=str(prog.business_request)
                prog_iter=str(prog.brand_iteration)
                prog_mkpl=str(prog.mkpl)
                prog_priority=str(prog.priority)
                h= str(prog.scrape_metric)
                k=str(prog.keys_count_gt_20)
                s=str(prog.ec_gv_matching_cvg_gt_20)
                prog_ssl_auto_kvp_status=str(prog.ssl_auto_kvp_status)
                prog_matching_status=str(prog.matching_status)
                prog_matching_gv_coverage=prog.matching_gv_coverage
                
                prog_incremental_sku_coverage=prog.incremental_sku_coverage

                prog_matching_sku_coverage=prog.matching_sku_coverage
                #prog_matching_status=prog.matching_status
                prog_incremental_matching_gv_coverage=prog.incremental_matching_gv_coverage
                prog_scrape_status=prog.scrape_status
                prog_first_level_ssp_status=prog.first_level_ssp_status
                prog_ptc_status=prog.ptc_status
                prog_backfill_status=prog.backfill_status
                prog_backfill_type=prog.backfill_type
                prog_overall_website_status=prog.overall_website_status
                prog_mp_id=prog.mp_id
                #print(h)
                #print(k)
                #print(s)
                
                print(prog_matching_gv_coverage)
                
                #if(ops_select.published_status=='completed'):

                #ops.save()       
                ops_select=brand_ops.objects.filter(ec_partition_id=prog_website_id)
                #print(ops_select[0].bid)              
                
                published_status=ops_select[0].published_status
                backfill_status=ops_select[0].backfill_status
                slots_backfilled_count=ops_select[0].slots_backfilled_count
                bem_converted=ops_select[0].bem_converted
                ops_ptc=ops_select[0].ptc_status
                ops_bem_status=ops_select[0].bem_status
                ops_backfill_status=ops_select[0].backfill_status
                ops_vv_nam_dropped=ops_select[0].vv_nam_dropped

                ops_bs_comments=str(ops_select[0].bs_comments)
                ops_bsv_comments=str(ops_select[0].bsv_comments)
                ops_ptc_comments=str(ops_select[0].ptc_comments)
                ops_ptv_comments=str(ops_select[0].ptv_comments)
                ops_backfill_comments=str(ops_select[0].backfill_comments)
                ops_bem_publish_comment=str(ops_select[0].bem_publish_comment)
                detailed_backfill_status_val='BS-'+ops_bs_comments+' |BSV-'+ops_bsv_comments+' |PTC-'+ops_ptc_comments+' |PTV-'+ops_ptv_comments+' |NMVV-'+ops_backfill_comments+' |BEM'+ops_bem_publish_comment
                ops_backfill_source_attributes_count=ops_select[0].backfill_source_attributes_count
                
                prog.ptc_status=ops_ptc
                prog.backfill_status=str(ops_backfill_status)
                prog.bem_status=ops_bem_status
                prog.priority='s'
                if(h=="Y" and s=="Y" and k=="Y"):
                    #print('hi')
                    pxrog.priority="P1"
                elif(h=="N" and s=="Y" and k=="Y"):
                    prog.priority="P2"
                elif(h=="N" and s=="Y" and k=="N"):
                    prog.priority="P3"
                elif(h=="Y" and s=="N" and k=="Y"):
                    prog.priority="P3"
                elif(h=="Y" and s=="Y" and k=="N"):
                    prog.priority="P3"
                elif(h=="N" and s=="N" and k=="Y"):
                    prog.priority="P3"
                elif(h=="N" and s=="N" and k=="N"):
                    prog.priority="P4"
                elif(h=="Y" and s=="N" and k=="N"):
                    prog.priority="P4"
                else:
                    prog.priority="YTD"
                if h=='Zero scrape':
                    prog.overall_website_status='Not successful on Scrape - All Scrapes done'
                #c1=prog_incremental_sku_coverage
                if(prog_incremental_sku_coverage=='' and prog_matching_sku_coverage==''):
                    if not(prog_matching_status==''):
                        prog.ec_gv_matching_cvg_gt_20=='YTC'
                elif(prog_incremental_sku_coverage>20 or prog_incremental_matching_gv_coverage>20):
                    prog.ec_gv_matching_cvg_gt_20=='Y'
                elif(prog_matching_gv_coverage>20 or prog_matching_sku_coverage>20):
                    prog.ec_gv_matching_cvg_gt_20=='Y'
                else:
                    prog.ec_gv_matching_cvg_gt_20=='N'

                if(published_status=='Completed'):
                    prog.overall_website_status='Backfilled'
                    prog.month=datetime.today()
                    if(slots_backfilled_count==0):
                        prog.overall_website_status='Backfilled with Zero slots - All Scrapes done'
                elif(backfill_status=='VV Completed'):
                    prog.overall_website_status='Backfill WIP - All Scrapes done'
                    prog.nm_status='NM WIP'
                    if(vv_nam_dropped=='yes'):
                        prog.overall_website_status='NameSpace Mapping dropped - All Scrapes done'
                if not(backfill_status is None):
                    if('ublished' in backfill_status):
                        prog.nm_status='NM WIP'
                #if not(ptc_status==''):
                    #if('ompleted' in ptc_status):
                        #prog.ptc_status='y'
                if(prog.flag_overall_website_status=='' or not(prog.flag_overall_website_status=='f1')):
                    if not(prog_scrape_status is None):
                        if(prog_ssl_auto_kvp_status=='Yes' or 'ompleted' in prog_scrape_status ):

                            if(prog_matching_status=='Yes' and s=='N' and (prog_matching_gv_coverage=='')):
                                prog.overall_website_status='Incremental Matching WIP'

                            if(prog_matching_status==''):
                                prog.overall_website_status='Matching WIP'
                            if(s=='Y' and k=='Y'):
                                prog.overall_website_status='Backfill YTS - All Scrapes done'

                        elif(not(prog_ssl_auto_kvp_status=='Yes') or 'ompleted' not in prog_scrape_status ):
                            prog.overall_website_status='Scrape WIP - SSL Pending'
                    else:
                        if(prog_ssl_auto_kvp_status=='Yes' ):

                            if(prog_matching_status=='Yes' and s=='N' and (prog_matching_gv_coverage=='')):
                                prog.overall_website_status='Incremental Matching WIP'

                            if(prog_matching_status==''):
                                prog.overall_website_status='Matching WIP'
                            if(s=='Y' and k=='Y'):
                                prog.overall_website_status='Backfill YTS - All Scrapes done'

                        elif(not(prog_ssl_auto_kvp_status=='Yes') or 'ompleted' not in prog_scrape_status ):
                            prog.overall_website_status='Scrape WIP - SSL Pending'
                        if not(prog_first_level_ssp_status=='SSP completed'):
                            prog.overall_website_status='Identity Scrape WIP'
                if(prog_ptc_status=='on hold'):
                    prog.overall_website_status='Brand Hold - Issues In PT-Classification'
                if(prog_backfill_status=='wip'):
                    prog.overall_website_status='Backfill WIP - All Scrapes done'
                if(ops_backfill_status=='VV completed'  ):
                    if(published_status=='' or published_status=='YTS' or published_status=='WIP'):
                        prog.overall_website_status='Publishing wip'
                    if ops_vv_nam_dropped=='yes':
                        prog.overall_website_status='NameSpace Mapping dropped - All Scrapes done'
                if(published_status=='completed'):
                    if(slots_backfilled_count==0):
                        prog.overall_website_status='Backfilled'
                    if(slots_backfilled_count>0):
                        prog.overall_website_status='Backfilled with Zero slots - All Scrapes done'
                if(prog_overall_website_status=='Backfilled with Zero slots - All Scrapes done' or prog_overall_website_status=='NameSpace Mapping dropped - All Scrapes done'):
                    prog.ds_queue='Yes'
                if (prog_mp_id in mp_id_chk):
                    prog.en_nonen='En'
                else:
                    prog.en_nonen='Non-En'
                #if not((bem_converted==0) or (bem_converted=='')):
                    #prog.is_bem_attempted='Yes'    
                #prog.save()
                
                #if(ops_select.published_status=='completed'):
                ops= brand_ops.objects.create(brand=prog_brand,website=prog_website,ec_partition_id=prog_website_id,language=prog_language,business_request=prog_bus_request,validation_sample_selection=ops_backfill_source_attributes_count,mkpl=prog_mkpl,backfill_type=prog_backfill_type,brand_iteration=prog_iter)
                
                ops.save()   
                prog.save()

        context = {'role':get_role(user),'sp_role2':get_sp_role2(user),'user':user,'summary':'summary','tot':'tot'}
        return render(request,'smt_smpo_dashboard/master_homepage.html',context)

def stakeholder(request):
    current_user = request.user
    user= current_user.username

    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    if not ob:
        return redirect('login')
    else:
        

        context = {'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user),'user':user,'summary':'summary','tot':'tot'}
        return render(request,'smt_smpo_dashboard/stakeholder_homepage.html',context)

def approve_adhoc(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    qs = productivity.objects.all().filter(brand="Adhoc",productivity__isnull=True)
    assos = []

    if not ob:
        return redirect('login')

    elif role_ob.user_role != "manager":
        return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        for i in qs.values('user').distinct():
            assos.append(list(i.values()))
        assos.sort()

        rda = request.GET.get('rda')
        if rda and rda != 'Choose...':
            qs = qs.filter(user=rda)

        master_list = []
        for ob in qs:
            ll = [ob.pid,ob.user,ob.timestamp]
            #ob.timestamp.date
            #sum_ob = productivity.objects.all().filter(brand="Adhoc",user=ob.user,timestamp__contains=str(ob.timestamp).split(' ')[0]).aggregate(Sum('productivity'))
            #productvty = sum_ob.get('productivity__sum')
            #ll.append((productvty))
            # adhoc info
            ll.append(ob.task)
            # adhoc comments
            ll.append(ob.sub_task)
            #requested adhoc_hours
            ll.append(ob.website)
            # owner
            ll.append(ob.brand_iteration)
            master_list.append(ll)

            if request.POST:
                #if condition for approve all button
                if str(request.POST.get('form_type'))=='approve':
                    for obj in qs:
                        obj.productivity = ob.website*60
                        obj.save()
                    return redirect('approve_adhoc')
                else:
                    ob = productivity.objects.get(pid=str(request.POST.get('id')))
                    print(ob.website)
                    if str(request.POST.get('status')) == "Approved":
                        if str(request.POST.get('hours')) != "0.00":
                            ob.website = str(request.POST.get('hours'))

                            ob.productivity = int(float(float(request.POST.get('hours'))*60))
                            ob.save()
                        else:
                            ob.productivity = int(float(float(ob.website))*60)
                            ob.save()
                    else:
                        #rejected adhoc
                        ob.productivity = 0
                        ob.save()
                    return redirect('approve_adhoc')
        context = {'role':get_role(user),'user':user,'obj':master_list,'assos':assos,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
        return render(request,'smt_smpo_dashboard/adhoc_approval_sheet.html',context)    
def attendence(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    role = get_role(user)

    if not ob:
        return redirect('login')

    elif role_ob.user_role != "manager"  :
        return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        template = 'smt_smpo_dashboard/attendence.html'
        attendence_list = []
        date_range = []  
        print_date_range = []
        day = []

        start_date=datetime.today()
        #print(start_date)
        
        start_date = start_date.replace(day=1)
        end_date=datetime.today()
        #end_date=end_date.replace(day=30)

        
        delta = timedelta(days=1)
        #print(delta)
        a=datetime.today()
        numdays = 30
        dateList = []
        for x in range (0, numdays):
            dateList.append((a + timedelta(days = x)).strftime("%Y-%m-%d"))
        #print(dateList)
        while start_date <= end_date:
            dd = calendar.day_name[start_date.weekday()]
            day.append(dd[:3])
            date_range.append(start_date.strftime("%Y-%m-%d"))
            print_date_range.append(start_date.strftime("%d-%b"))   
            print(print_date_range)
            start_date += delta
        attendence_list=create_attendence(date_range)
        context = {'role':role,'user':user,'attendence_list':attendence_list,'date_range':print_date_range,'day':day,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}

        if request.POST:
            start_date=request.POST.get('startDate')
            start_date= datetime.strptime(start_date,'%Y-%m-%d')
            end_date=request.POST.get('endDate')
            end_date= datetime.strptime(end_date,'%Y-%m-%d')
        
            date_range = []
            print_date_range = []
            day = []
            while start_date <= end_date:
                dd = calendar.day_name[start_date.weekday()]
                day.append(dd[:3])
                date_range.append(start_date.strftime("%Y-%m-%d"))
                print_date_range.append(start_date.strftime("%d-%b"))   
                start_date += delta

            attendence_list=[]
            attendence_list=create_attendence(date_range)
        
            context = {'role':role,'user':user,'attendence_list':attendence_list,'date_range':print_date_range,'day':day,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
        return render(request,template,context)

def hist_adhoc(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    qs = productivity.objects.all().filter(brand='Adhoc',productivity__isnull=False)
    assos = []

    if not ob:
        return redirect('login')

    elif role_ob.user_role != "manager":
        return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        for i in qs.values('user').distinct():
            assos.append(list(i.values()))
    
        rda = request.GET.get('rda')
        etadate_min = request.GET.get('date_min')
        etadate_max = request.GET.get('date_max')

        if rda and rda != 'Choose...':
            qs = qs.filter(user=rda)
    
        if etadate_min:
            qs = qs.filter(timestamp__gte=etadate_min)

        if etadate_max:
            qs = qs.filter(timestamp__lte=etadate_max)

        return render(request,'smt_smpo_dashboard/hist_adhoc.html',{'obj':qs,'RDA':assos,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)})

def auditor(request):
    current_user = request.user
    user = current_user.username

    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    #print(role_ob.special_role1)
    if not ob:
        return redirect('login')
    else:
        date_range = []
        delta = timedelta(days=1)

        start_date=datetime.today()
        start_date = start_date.replace(month=1)
        end_date=datetime.today().month
        #print(end_date)
        #print(start_date.month+1)
        #print(start_date.strftime("%Y-%m"))
        m=2

        while m <= end_date:
            #print(m)
            if(m<12):
                date_range.append(start_date.strftime("%Y-%m"))   
                start_date=start_date.replace(month=m)
            #print(start_date)
            m+=1
        #print(date_range)
        master_list,total = create_homepage_cost([user],date_range)
        #print(master_list)
        master_list2=[]
        for l in master_list:
            #print([l[17:]])
            master_list2.append(l[2:])
        #print(master_list2)
        return render(request,'smt_smpo_dashboard/audit_homepage.html',{'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user),'user':user,'summary':'summary','tot':'tot','sp-role':role_ob.special_role1,'master_list':master_list2})
def sme(request):
    current_user = request.user
    user = current_user.username

    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    if not ob:
        return redirect('login')
    else:
        date_range = []
        delta = timedelta(days=1)

        start_date=datetime.today()
        start_date = start_date.replace(month=1)
        end_date=datetime.today().month
        #print(start_date.month+1)
        #print(start_date.strftime("%Y-%m"))
        m=2

        while m <= end_date:
            #print(m)
            if(m<12):
                date_range.append(start_date.strftime("%Y-%m"))   
                start_date=start_date.replace(month=m)
            #print(start_date)
            m+=1
        #print(date_range)
        master_list,total = create_homepage_cost([user],date_range)
        #print(master_list)
        master_list2=[]
        for l in master_list:
            #print([l[17:]])
            master_list2.append(l[2:])
        #print(master_list2)
        return render(request,'smt_smpo_dashboard/sme_homepage.html',{'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user),'user':user,'summary':'summary','tot':'tot','master_list':master_list2})

def create_attendence(date_range):
    print(date_range)
    user = []
    obj = profile.objects.all()
    for i in obj:
        user.append(i.user_name.strip())
    user.sort()
    attendence_list = []
    for u in user:
        a=[]
        tem=[]
        p,l,wfh = 0,0,0
        for dd in date_range:
            atten_obj = productivity.objects.all().filter(brand="Login",user=u,timestamp__contains=dd)
            if atten_obj.count() == 0:
                dt = datetime.strptime(dd,'%Y-%m-%d')
                #print(dt)
                holiday = calendar.day_name[dt.weekday()]
                if holiday[:3]=='Sat' or holiday[:3]=='Sun':
                    status = '<font color="green">'+"WO"+'</font>'
                else:
                    status = '<font color="red">'+"L"+'</font>'
                    p+=1
            elif atten_obj.count() == 1:
                ob = productivity.objects.get(brand="Login",user=u,timestamp__contains =dd)
                status=ob.sub_task
                if status == "Half Day":
                    l +=1
                    status = "HD"
                elif status == "Work from Office":
                    status = "P"
                elif status == "Work from Home":
                    status = "WFH" 
                    wfh+=1
                elif status == "Holiday":
                    status = "H"
                else:
                    l+=1 
                    status = "LL"
            else:
                obj = productivity.objects.all().filter(user=u,timestamp__contains=dd)
                ob = obj[0]
                status=ob.sub_task
                if status == "Half Day":
                    l +=1
                    status = "HD"
                elif status == "Work from Office":
                    status = "P"
                elif status == "Work from Home":
                    status = "WFH" 
                    wfh+=1
                elif status == "Holiday":
                    status = "H"
                else:
                    l+=1 
                    status = "LL"
            a.append(status)
        tem = [u,p,l,wfh]
        for i in a:
            tem.append(i)
        attendence_list.append(tem)
    return attendence_list

def leave_planner(request):
	current_user = request.user
	user = current_user.username
	start_date=request.POST.get('startDate')
	mgr=request.POST.get('Owner')
	#end_date=request.POST.get('endDate')
	today = datetime.today()
	ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
	role_ob = profile.objects.get(user_name=user)
	#print(ob)
	if not ob:

		return redirect('login')
        #print('hi')
	else:
		owner = []
		rol = profile.objects.all().filter(user_role='manager')
		for i in rol:
			owner.append(i.user_name)
		if request.POST:
			ob = productivity.objects.create(brand="leave planned",user=user,timestamp=start_date,brand_iteration=mgr)
			ob.save()
			if role_ob.user_role == "manager":
				planner_obj = productivity.objects.all().filter(brand="leave planned",brand_iteration=user)
			else:
				planner_obj = productivity.objects.all().filter(brand="leave planned",user=user)
			
			context = {'user':user,'owner':owner,'planner':planner_obj,'role':role_ob.user_role,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
			return render(request,'smt_smpo_dashboard/leave_planner.html',context)
		else:
			if role_ob.user_role == "manager":
				planner_obj = productivity.objects.all().filter(brand="leave planned")
			else:
				planner_obj = productivity.objects.all().filter(brand="leave planned",user=user)
			
			context = {'user':user,'owner':owner,'planner':planner_obj,'role':role_ob.user_role,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
        
			#print(planner_obj.query)
			return render(request,'smt_smpo_dashboard/leave_planner.html',context)

def view_planner(request):
    current_user = request.user
    user = current_user.username
    start_date=request.POST.get('startDate')
    #mgr=request.POST.get('Owner')
    #end_date=request.POST.get('endDate')
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    role = get_role(user)
    if not ob:
        return redirect('login')

    elif role_ob.user_role != "manager"  :
        return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        template = 'smt_smpo_dashboard/view_planner.html'
        attendence_list = []
        date_range = []  
        print_date_range = []
        day = []
        delta = timedelta(days=1)

        a=datetime.today()
        numdays = 30
        dateList = []
        for x in range (0, numdays):
            dateList.append((a + timedelta(days = x)).strftime("%Y-%m-%d"))
            print_date_range.append((a + timedelta(days = x)).strftime("%d-%b"))
        #print(dateList)

        attendence_list=create_lp(dateList)
        context = {'role':role,'user':user,'attendence_list':attendence_list,'date_range':print_date_range,'day':day,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}

        if request.POST:
            start_date=request.POST.get('startDate')
            start_date= datetime.strptime(start_date,'%Y-%m-%d')
            end_date=request.POST.get('endDate')
            end_date= datetime.strptime(end_date,'%Y-%m-%d')
        
            date_range = []
            print_date_range = []
            day = []
            while start_date <= end_date:
                dd = calendar.day_name[start_date.weekday()]
                day.append(dd[:3])
                date_range.append(start_date.strftime("%Y-%m-%d"))
                print_date_range.append(start_date.strftime("%d-%b"))   
                start_date += delta

            attendence_list=[]
            attendence_list=create_lp(date_range)
        
            context = {'role':role,'user':user,'attendence_list':attendence_list,'date_range':print_date_range,'day':day,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
        return render(request,template,context)
    

def create_lp(date_range):
    user = []
    obj = profile.objects.all()
    for i in obj:
        user.append(i.user_name.strip())
    user.sort()
    attendence_list = []
    for u in user:
        a=[]
        tem=[]
        pl = 0
        for dd in date_range:
            atten_obj = productivity.objects.all().filter(brand="leave planned",user=u,timestamp__contains=dd)
            if atten_obj.count() == 0:
                dt = datetime.strptime(dd,'%Y-%m-%d')
                holiday = calendar.day_name[dt.weekday()]
                if holiday[:3]=='Sat' or holiday[:3]=='Sun':
                    status = '<font color="green">'+"WO"+'</font>'
                else:
                    status = ''
                    #p+=1
            elif atten_obj.count() == 1:
                ob = productivity.objects.get(brand="leave planned",user=u,timestamp__contains =dd)
                pl+=1 
                status = "PL"
            
            a.append(status)
        tem = [pl,u]
        for i in a:
            tem.append(i)
        attendence_list.append(tem)
    return attendence_list    
def log_atten(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')

    else:
        usr = []
        obj = profile.objects.all()
        for i in obj:
            usr.append(i.user_name.strip())
        usr.sort()

        midday = datetime.strptime('11:00:00', '%H:%M:%S')
        midday = datetime.time(midday)

        qs = productivity.objects.all().filter(brand="Login")

        rda = request.GET.get('rda')
        etadate_min = request.GET.get('date_min')
        etadate_max = request.GET.get('date_max')

        if rda and rda != 'Choose...':
            qs = qs.filter(user=rda)
        if etadate_min:
            qs = qs.filter(timestamp__gte=etadate_min)

        if etadate_max:
            qs = qs.filter(timestamp__lte=etadate_max)

        if request.POST:
            if str(request.POST.get('form_type'))=='add':
                if str(request.POST.get('action'))=="Work from Home" or str(request.POST.get('action'))=="Work from Office":
                    obj= productivity.objects.create(brand="Login",user=str(request.POST.get('ass')),sub_task=str(request.POST.get('action')),timestamp=datetime.combine(datetime.strptime(str(request.POST.get('date')), '%Y-%m-%d'),midday),productivity=int(8)*60)
                    obj.save()
                else:
                    obj= productivity.objects.create(brand="Login",user=str(request.POST.get('ass')),sub_task=str(request.POST.get('action')),timestamp=datetime.combine(datetime.strptime(str(request.POST.get('date')), '%Y-%m-%d'),midday),productivity=int(4)*60)
                    obj.save()
                return render(request,'smt_smpo_dashboard/log_attendence.html',{'qs':qs.all().order_by("-timestamp")[:20],'RDA':usr,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)})
            elif str(request.POST.get('form_type'))=='holiday':
                for i in usr:
                    obj= productivity.objects.create(brand="Login",user=i,sub_task="Holiday",timestamp=datetime.combine(datetime.strptime(str(request.POST.get('date')), '%Y-%m-%d'),midday),productivity=int(0))
                    obj.save()
                return render(request,'smt_smpo_dashboard/log_attendence.html',{'qs':qs.all().order_by("-timestamp")[:20],'RDA':usr,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)})
            else:
                ob = productivity.objects.filter(pid=str(request.POST.get('id'))).delete()
                return render(request,'smt_smpo_dashboard/log_attendence.html',{'qs':qs.all().order_by("-timestamp")[:20],'RDA':usr,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)})
        return render(request,'smt_smpo_dashboard/log_attendence.html',{'qs':qs.all().order_by("-timestamp")[:20],'RDA':usr,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)})  


#def view_db(request):
    #current_user = request.user
    #user= current_user.username
    #context = {'hi':'hi'}
    #return render(request,'smt_smpo_dashboard/website_db.html',context)
def view_db(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')

    #elif role_ob.special_role1 != "lead":
        #return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        qs = brand_ops.objects.all()
        brand = request.GET.get('brand')
        brand_iteration = request.GET.get('brand_iteration')
        backfill_type = request.GET.get('backfill_type')
        language = request.GET.get('language')
        #month = request.GET.get('month')
        bs_status = request.GET.get('bs_status')
        date_min = request.GET.get('date_min')
        ssl_completed_date = request.GET.get('ssl_completed_date')
        matching_completed_date = request.GET.get('matching_completed_date')
        incremental_matching_completed_date = request.GET.get('incremental_matching_completed_date')
        bsv_status = request.GET.get('bsv_status')
        ptc_status = request.GET.get('ptc_status')
        ptv_status = request.GET.get('ptv_status')
        ec_partition_id= request.GET.get('ec_partition_id')
        backfill_status = request.GET.get('backfill_status')
        bem_status = request.GET.get('bem_status')
        published_status = request.GET.get('published_status')
        published_allocation_date = request.GET.get('published_allocation_date')
        business_request= request.GET.get('business_request')
        backfill_type= request.GET.get('backfill_type')
        brand_iteration= request.GET.get('brand_iteration')

        if brand:
            qs = qs.filter(brand__icontains=brand)

        if brand_iteration:
            qs = qs.filter(brand_iteration__icontains=brand_iteration)

        if backfill_type:
            qs = qs.filter(backfill_type__icontains=backfill_type)

        if language:
            qs = qs.filter(language__icontains=language)

        #if month:
            #qs = qs.filter(month__icontains=month)

        if bs_status:
            qs = qs.filter(bs_status__icontains=bs_status)

        if date_min:
            qs = qs.filter(date_min__icontains=date_min)

        if ssl_completed_date:
            qs = qs.filter(ssl_completed_date__icontains=ssl_completed_date)

        if matching_completed_date:
            qs = qs.filter(matching_completed_date__icontains=matching_completed_date)

        if incremental_matching_completed_date:
            qs = qs.filter(incremental_matching_completed_date__icontains=incremental_matching_completed_date)
            
        if bsv_status:
            qs = qs.filter(bsv_status__icontains=bsv_status)

        if ptc_status:
            qs = qs.filter(ptc_status__icontains=ptc_status)

        if ptv_status:
            qs = qs.filter(ptv_status__icontains=ptv_status)

        if ec_partition_id:
            qs = qs.filter(ec_partition_id__icontains=ec_partition_id)
            
        if backfill_status:
            qs = qs.filter(backfill_status__icontains=backfill_status)

        if bem_status:
            qs = qs.filter(bem_status__icontains=bem_status)

        if published_status:
            qs = qs.filter(published_status__icontains=published_status)

        if published_allocation_date:
            qs = qs.filter(published_allocation_date__icontains=published_allocation_date)
            
        if business_request:
            qs = qs.filter(business_request__icontains=business_request)

        if backfill_type:
            qs = qs.filter(backfill_type__icontains=backfill_type)

        if brand_iteration:
            qs = qs.filter(brand_iteration__icontains=brand_iteration)

        if request.POST:
        	#print(list(qs.values()))
        	df_output = pd.DataFrame(list(qs.values())) 
        	excel_file = IO()
        	xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        	df_output.to_excel(xlwriter, 'sheetname')

        	xlwriter.save()
        	xlwriter.close()
        	excel_file.seek(0)
        	response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        	response['Content-Disposition'] = 'attachment; filename=myfile.xlsx'
        	return response


        context = {'object':qs.all()[0:20]}
        return render(request,'smt_smpo_dashboard/website_db.html',context)

def view_db2(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')

    #elif role_ob.special_role1 != "lead":
        #return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        qs = brand_program.objects.all()
        brand = request.GET.get('brand')
        brand_iteration = request.GET.get('brand_iteration')
        backfill_type = request.GET.get('backfill_type')
        language = request.GET.get('language')
        month = request.GET.get('month')
        first_level_ssp_status = request.GET.get('first_level_ssp_status')
        date_min = request.GET.get('date_min')
        program_usecase = request.GET.get('program_usecase')
        mkpl = request.GET.get('mkpl')
        keys_available_website_count = request.GET.get('keys_available_website_count')
        scrape_metric = request.GET.get('scrape_metric')
        is_backfill = request.GET.get('is_backfill')
        keys_count = request.GET.get('keys_count')
        keys_count_gt_20= request.GET.get('keys_count_gt_20')
        uec_reflection_status = request.GET.get('uec_reflection_status')
        ssl_auto_kvp_status = request.GET.get('ssl_auto_kvp_status')
        brand_status = request.GET.get('brand_status')
        business_request= request.GET.get('business_request')
        backfill_type= request.GET.get('backfill_type')
        brand_iteration= request.GET.get('brand_iteration')

        if brand:
            qs = qs.filter(brand__icontains=brand)

        if brand_iteration:
            qs = qs.filter(brand_iteration__icontains=brand_iteration)

        if backfill_type:
            qs = qs.filter(backfill_type__icontains=backfill_type)

        if language:
            qs = qs.filter(language__icontains=language)

        if month:
            qs = qs.filter(month__icontains=month)

        if first_level_ssp_status:
            qs = qs.filter(first_level_ssp_status__icontains=first_level_ssp_status)

        if date_min:
            qs = qs.filter(date_min__icontains=date_min)

        if program_usecase:
            qs = qs.filter(program_usecase__icontains=program_usecase)

        if mkpl:
            qs = qs.filter(mkpl__icontains=mkpl)

        if keys_available_website_count:
            qs = qs.filter(keys_available_website_count__icontains=keys_available_website_count)
            
        if scrape_metric:
            qs = qs.filter(scrape_metric__icontains=scrape_metric)

        if is_backfill:
            qs = qs.filter(is_backfill__icontains=is_backfill)

        if keys_count:
            qs = qs.filter(keys_count__icontains=keys_count)

        if keys_count_gt_20:
            qs = qs.filter(keys_count_gt_20__icontains=keys_count_gt_20)
            
        if uec_reflection_status:
            qs = qs.filter(uec_reflection_status__icontains=uec_reflection_status)

        if ssl_auto_kvp_status:
            qs = qs.filter(ssl_auto_kvp_status__icontains=ssl_auto_kvp_status)

        

        if brand_status:
            qs = qs.filter(brand_status__icontains=brand_status)
            
        if business_request:
            qs = qs.filter(business_request__icontains=business_request)

        if backfill_type:
            qs = qs.filter(backfill_type__icontains=backfill_type)

        if brand_iteration:
            qs = qs.filter(brand_iteration__icontains=brand_iteration)

        if request.POST:
            df_output = pd.DataFrame(list(qs.values())) 
            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df_output.to_excel(xlwriter, 'sheetname')

            xlwriter.save()
            xlwriter.close()
            excel_file.seek(0)
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=myfile.xlsx'
            return response


        context = {'object':qs.all()[0:20]}
        return render(request,'smt_smpo_dashboard/brand_db.html',context)
def user_role(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    obj = profile.objects.all().order_by('user_role')

    if not ob:
        return redirect('login')

    elif role_ob.user_role != "manager":
        return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        if request.POST:
            if str(request.POST.get('form_type'))=='del':
                ob = profile.objects.filter(uid=str(request.POST.get('id'))).delete()
            else:
                log = profile.objects.create(user_name=str(request.POST.get('user')),user_role=str(request.POST.get('role')),special_role1=str(request.POST.get('srole1')),special_role2=str(request.POST.get('srole2')))
                log.save()
        context = {'role':"manager",'user':user,'obj': obj,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
        return render(request,'smt_smpo_dashboard/user_role.html',context)
def usr_pro(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    template = 'smt_smpo_dashboard/productivity.html'
    yesterday_date = [datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')]

    if not ob:
        return redirect('login')

    elif role_ob.user_role != "manager":
        return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        if request.POST:
            start_date=request.POST.get('startDate')
            start_date= datetime.strptime(start_date,'%Y-%m-%d')
            end_date=request.POST.get('endDate')
            end_date= datetime.strptime(end_date,'%Y-%m-%d')

            delta = timedelta(days=1)
            date_range = []
            print_date_range =[]
            while start_date <= end_date:
                date_range.append(start_date.strftime("%Y-%m-%d"))
                print_date_range.append(start_date.strftime("%d-%b")) 
                start_date += delta
            return render(request,template,{'role':get_role(user),'user':user,'prod':productivity_calculator(date_range),'date_range':print_date_range,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)})
     
        return render(request,template,{'role':get_role(user),'user':user,'prod':productivity_calculator(yesterday_date),'date_range':yesterday_date,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)})
def productivity_calculator(date_range):
    usr = []
    for ob in profile.objects.all().exclude(user_role="manager"):
        usr.append(ob.user_name)

    master_list = []
    for associate in usr:
        u =[]
        tp,tb =0,0
        u = [associate]
        for yesterday_date in date_range:           
            productvty = productivity.objects.filter(user=associate,timestamp__contains=yesterday_date).exclude(brand="Login").aggregate(Sum('productivity'))
            productvty = productvty.get('productivity__sum')
            if productvty is None:
                prod_value = 0
            else:
                tp += int(productvty)
                prod_value = int(productvty)
            
            ben_ob = productivity.objects.all().filter(brand="Login",user=associate,timestamp__contains=yesterday_date).count()
            if ben_ob == 0:
                benchmark_var = 0
                u.append('L')
            else:
                ob=productivity.objects.get(brand="Login",user=associate,timestamp__contains=yesterday_date)
                tb += int(ob.productivity)
                benchmark_var = int(ob.productivity)
                if benchmark_var == 0:
                   u.append("H")
                else: 
                   u.append(round((prod_value/benchmark_var)*100,2))

        if tb == 0:
            u.append('<font color="blue"><b>'+"0%"+'</b></font>')
        else:
            tot = tp/tb
            u.append('<font color="blue"><b>'+str(int(tot*100))+"%"+'</b></font>')

        master_list.append(u)
    return master_list
def assos_details(request):
    current_user = request.user
    user= current_user.username

    usr_list = get_rda()
    for i in get_auditor():
        usr_list.append(i)

    mast_list = []
    tot = []
    date_range = []
    print_date_range = []
    delta = timedelta(days=1)
    
    if request.POST:
        start_date=request.POST.get('startDate')
        start_date= datetime.strptime(start_date,'%Y-%m-%d')
        end_date=request.POST.get('endDate')
        end_date= datetime.strptime(end_date,'%Y-%m-%d')
        u = [request.POST.get('ass')]

        while start_date <= end_date:
            dd = calendar.day_name[start_date.weekday()]
            date_range.append(start_date.strftime("%Y-%m-%d"))
            print_date_range.append(start_date.strftime("%d-%b"))   
            start_date += delta
        mast_list,tot = create_cost(u,date_range)
      
        context = {'user':user,'master_list':mast_list,'total':tot,'RDA':usr_list,'role':get_role(user)}
        return render(request,'smt_smpo_dashboard/user_wise_detail.html',context)

    context = {'user':user,'master_list':mast_list,'total':tot,'RDA':usr_list,'role':get_role(user)}
    return render(request,'smt_smpo_dashboard/user_wise_detail.html',context)

def daily_cost(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    usr_list = get_rda()

    if not ob:
        return redirect('login')

    elif role_ob.user_role != "manager":
        return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        for i in get_auditor():
            usr_list.append(i)
        today = datetime.today()
        master_list,tot = create_cost(usr_list,[today.strftime("%Y-%m-%d")])

        if request.POST:
            dt=request.POST.get('startDate')
            date = datetime.strptime(dt,'%Y-%m-%d')
            master_list,tot = create_cost(usr_list,[datetime.strftime(date,'%Y-%m-%d')])
            context1 = {'role':get_role(user),'user':user,'master_list':master_list,'today_date':datetime.strptime(dt,'%Y-%m-%d'),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
            return render(request,'smt_smpo_dashboard/daily_cost.html',context1) 

        context = {'role':get_role(user),'user':user,'master_list':master_list,'today_date':datetime.today(),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
        return render(request,'smt_smpo_dashboard/daily_cost.html',context) 
def create_cost(users_list,date_range):
    master_list = []
    total = []
    t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13 = 0,0,0,0,0,0,0,0,0,0,0,0,0
    p,l,hd,wl = 0,0,0,0
    for user in users_list:
        for today_date in date_range:
            usr_list = []
            prod_val = 0
            benchmark_var = 0

            usr_list.append('<b>'+user+'</b>')
            usr_list.append(get_role(user))
            usr_list.append(today_date)

            feas = productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='Brand study',sub_task='Completed').count()
            feas_ob = productivity.objects.filter(user=user,timestamp__contains=today_date,task='Brand study',sub_task='Completed').aggregate(Sum('productivity'))
            productvty = feas_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t1+=feas 
            usr_list.append(feas)

            cr = productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='Brand study validation',sub_task__startswith='Completed').count()
            cr_ob = productivity.objects.filter(user=user,timestamp__contains=today_date,task='Brand study validation',sub_task__startswith='Completed').aggregate(Sum('productivity'))
            productvty = cr_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t2+= cr
            usr_list.append(cr)

            cr_review = productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='PTC',sub_task__startswith='Completed').count()
            cr_review_ob1 = productivity.objects.filter(user=user,timestamp__contains=today_date,task='PTC',sub_task__startswith='Completed').aggregate(Sum('productivity'))
            productvty = cr_review_ob1.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            
            else:
                prod_val += int(productvty)
                t3+= cr_review
            usr_list.append(cr_review)

            cr_review_ob2 = productivity.objects.filter(user=user,timestamp__contains=today_date,task='PTV',sub_task__startswith='Completed').count()
            crawl_ob2 = productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='PTV',sub_task__startswith='Completed').aggregate(Sum('productivity'))
            productvty = crawl_ob2.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t4+= cr_review_ob2 
            usr_list.append(cr_review_ob2)

            crawl = productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='Backfill - DQ',sub_task='VV completed').count()
            crawl_ob = productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='Backfill - DQ',sub_task='VV completed').aggregate(Sum('productivity'))
            productvty = crawl_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t4+= crawl 
            usr_list.append(crawl)

            scrape = productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='Backfill - DQ',sub_task__startswith='BEM completed').count()
            scrape_ob = productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='Backfill - DQ',sub_task__startswith='BEM completed').aggregate(Sum('productivity'))
            productvty = scrape_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t5+= scrape 
            usr_list.append(scrape)

            reconf = productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='Publised with ion file').count()
            reconf_ob = productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='Publised with ion file').aggregate(Sum('productivity'))
            productvty = reconf_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t6+= reconf 
            usr_list.append(reconf)

            reconf_a = productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='VV completed').count()
            reconf_a_ob = productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='VV completed').aggregate(Sum('productivity'))
            productvty = reconf_a_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t7+= reconf_a
            usr_list.append(reconf_a)

            apprvd = productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='BEM completed').count()
            apprvd_ob = productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='BEM completed').aggregate(Sum('productivity'))
            productvty = apprvd_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t8+= apprvd 
            usr_list.append(apprvd)
            
            #aoa
            count_aoa= productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='Backfill - DQ',sub_task__startswith='Published').count()
            aoa_ob = productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='Backfill - DQ',sub_task='Published').aggregate(Sum('productivity'))
            aoa = aoa_ob.get('productivity__sum')
            if aoa is None:
                prod_val += 0
            else:
                prod_val += int(aoa)
                t9+= count_aoa
            usr_list.append(count_aoa)

            #asins
            #asin_ob = productivity.objects.all().filter(user=user,timestamp__contains=today_date,task='',sub_task__startswith='asin').aggregate(Sum('task'))
            #asin = asin_ob.get('task__sum')
            #value_productivity = benchmark.objects.all().filter(task="Asin")
            #print(value_productivity)
            #if asin is None:
                #prod_val += 0
                #usr_list.append(0)
            #else:
                #prod_val += int(asin)*value_productivity.productivity
                #t10+= int(asin)
                #usr_list.append(int(asin))
            

            #adhoc
            adhoc_ob = productivity.objects.all().filter(user=user,timestamp__contains=today_date,brand='Adhoc').aggregate(Sum('productivity'))
            adhoc = adhoc_ob.get('productivity__sum')
            comp_ob = productivity.objects.all().filter(user=user,timestamp__contains=today_date,sub_task='Complexity Hours').aggregate(Sum('productivity'))
            comp = comp_ob.get('productivity__sum')
            if adhoc is None:
                prod_val += 0
                hours = 0
            else:
                prod_val += int(adhoc)
                hours = int(adhoc)/60

            if comp is None:
                prod_val += 0
                hours1 = 0
            else:
                prod_val += int(comp)
                hours1 = int(comp)/60
            t11+= hours+hours1
            usr_list.append(hours+hours1)

            #total
            t12+= prod_val
            usr_list.append(round(prod_val/60,2))

            #benchmark_hours
            ben_ob = productivity.objects.all().filter(brand="Login",user=user,timestamp__contains=today_date).count()
            if ben_ob == 0:
                usr_list.append(0)
                benchmark_var = 0
            else:
                ob=productivity.objects.get(brand="Login",user=user,timestamp__contains=today_date)
                usr_list.append(int(ob.productivity)/60)
                benchmark_var = int(ob.productivity)
                t13+= int(ob.productivity)
            
            #productivity%
            bench_min = int(benchmark_var)
            if bench_min == 0:
                percent = 0
            else:
                percent = (prod_val/bench_min)*100
            usr_list.append(str(round(percent,2))+"%")
            
            #comment
            if benchmark_var==0:
                holiday = calendar.day_name[(datetime.strptime(today_date,"%Y-%m-%d")).weekday()]
                if holiday[:3]=='Sat' or holiday[:3]=='Sun':
                    wl+=1
                    usr_list.append("WO")
                else:
                    l+=1
                    usr_list.append('<font color="red">'+"L"+'</font>')    
            elif benchmark_var==4:
                hd+=1
                usr_list.append('<font color="blue">'+"HD"+'</font>')
            else:
                p+=1
                usr_list.append('<font color="green">'+"P"+'</font>')

            master_list.append(usr_list)
    if t13 == 0:
       tt1 = 0
    else:
       tt1 = round((t12/t13)*100,2)
    total = ["<b>Total</b>","","",t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,round(t12/60,2),round(t13/60,2),tt1,'<font color="green">'+str(p)+'</font>'+"/"+'<font color="blue">'+str(hd)+'</font>'+"/"+'<font color="red">'+str(l)+'</font>']
    return master_list,total

def sod_cost(users_list,date_range):
    master_list = []
    total = []
    t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13 = 0,0,0,0,0,0,0,0,0,0,0,0,0
    p,l,hd,wl = 0,0,0,0
    print(date_range)
    for user in users_list:
        for today_date in date_range:
            usr_list = []
            prod_val = 0
            benchmark_var = 0

            usr_list.append('<b>'+user+'</b>')
            usr_list.append(get_role(user))
            usr_list.append(today_date)

            feas = productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='Brand study',sub_task__isnull=False).count()
            feas_ob = productivity.objects.filter(user=user,timestamp__lte=today_date,task='Brand study',sub_task__isnull=False).aggregate(Sum('productivity'))
            productvty = feas_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t1+=feas 
            usr_list.append(feas)

            cr = productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='Brand study validation',sub_task__isnull=False).count()
            cr_ob = productivity.objects.filter(user=user,timestamp__lte=today_date,task='Brand study validation',sub_task__isnull=False).aggregate(Sum('productivity'))
            productvty = cr_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t2+= cr
            usr_list.append(cr)

            cr_review = productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='PTC',sub_task__isnull=False).count()
            cr_review_ob1 = productivity.objects.filter(user=user,timestamp__lte=today_date,task='PTC',sub_task__isnull=False).aggregate(Sum('productivity'))
            productvty = cr_review_ob1.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            
            else:
                prod_val += int(productvty)
                t3+= cr_review
            usr_list.append(cr_review)

            cr_review_ob2 = productivity.objects.filter(user=user,timestamp__lte=today_date,task='PTV',sub_task__isnull=False).count()
            crawl_ob2 = productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='PTV',sub_task__isnull=False).aggregate(Sum('productivity'))
            productvty = crawl_ob2.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t4+= cr_review_ob2 
            usr_list.append(cr_review_ob2)

            crawl = productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='Backfill - DQ',sub_task__isnull=False).count()
            crawl_ob = productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='Backfill - DQ',sub_task__isnull=False).aggregate(Sum('productivity'))
            productvty = crawl_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t4+= crawl 
            usr_list.append(crawl)

            scrape = productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='Backfill - DQ',sub_task__isnull=False).count()
            scrape_ob = productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='Backfill - DQ',sub_task__isnull=False).aggregate(Sum('productivity'))
            productvty = scrape_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t5+= scrape 
            usr_list.append(scrape)

            reconf = productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='Backfill - Manual',sub_task__isnull=False).count()
            reconf_ob = productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='Backfill - Manual',sub_task__isnull=False).aggregate(Sum('productivity'))
            productvty = reconf_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t6+= reconf 
            usr_list.append(reconf)

            reconf_a = productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='Backfill - Manual',sub_task__isnull=False).count()
            reconf_a_ob = productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='Backfill - Manual',sub_task__isnull=False).aggregate(Sum('productivity'))
            productvty = reconf_a_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t7+= reconf_a
            usr_list.append(reconf_a)

            apprvd = productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='Backfill - Manual',sub_task__isnull=False).count()
            apprvd_ob = productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='Backfill - Manual',sub_task__isnull=False).aggregate(Sum('productivity'))
            productvty = apprvd_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t8+= apprvd 
            usr_list.append(apprvd)
            
            #aoa
            count_aoa= productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='Backfill - DQ',sub_task__isnull=False).count()
            aoa_ob = productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='Backfill - DQ',sub_task__isnull=False).aggregate(Sum('productivity'))
            aoa = aoa_ob.get('productivity__sum')
            if aoa is None:
                prod_val += 0
            else:
                prod_val += int(aoa)
                t9+= count_aoa
            usr_list.append(count_aoa)

            #asins
            #asin_ob = productivity.objects.all().filter(user=user,timestamp__lte=today_date,task='',sub_task__startswith='asin').aggregate(Sum('task'))
            #asin = asin_ob.get('task__sum')
            #value_productivity = benchmark.objects.all().filter(task="Asin")
            #print(value_productivity)
            #if asin is None:
                #prod_val += 0
                #usr_list.append(0)
            #else:
                #prod_val += int(asin)*value_productivity.productivity
                #t10+= int(asin)
                #usr_list.append(int(asin))
            

            #adhoc
            adhoc_ob = productivity.objects.all().filter(user=user,timestamp__lte=today_date,brand='Adhoc').aggregate(Sum('productivity'))
            adhoc = adhoc_ob.get('productivity__sum')
            comp_ob = productivity.objects.all().filter(user=user,timestamp__lte=today_date,sub_task='Complexity Hours').aggregate(Sum('productivity'))
            comp = comp_ob.get('productivity__sum')
            if adhoc is None:
                prod_val += 0
                hours = 0
            else:
                prod_val += int(adhoc)
                hours = int(adhoc)/60

            if comp is None:
                prod_val += 0
                hours1 = 0
            else:
                prod_val += int(comp)
                hours1 = int(comp)/60
            t11+= hours+hours1
            usr_list.append(hours+hours1)

            #total
            t12+= prod_val
            usr_list.append(round(prod_val/60,2))

            #benchmark_hours
            ben_ob = productivity.objects.all().filter(brand="Login",user=user,timestamp__lte=today_date).count()
            if ben_ob == 0:
                usr_list.append(0)
                benchmark_var = 0
            else:
                ob=productivity.objects.get(brand="Login",user=user,timestamp__lte=today_date)
                usr_list.append(int(ob.productivity)/60)
                benchmark_var = int(ob.productivity)
                t13+= int(ob.productivity)
            
            #productivity%
            bench_min = int(benchmark_var)
            if bench_min == 0:
                percent = 0
            else:
                percent = (prod_val/bench_min)*100
            usr_list.append(str(round(percent,2))+"%")
            
            #comment
            if benchmark_var==0:
                holiday = calendar.day_name[(datetime.strptime(today_date,"%Y-%m-%d")).weekday()]
                if holiday[:3]=='Sat' or holiday[:3]=='Sun':
                    wl+=1
                    usr_list.append("WO")
                else:
                    l+=1
                    usr_list.append('<font color="red">'+"L"+'</font>')    
            elif benchmark_var==4:
                hd+=1
                usr_list.append('<font color="blue">'+"HD"+'</font>')
            else:
                p+=1
                usr_list.append('<font color="green">'+"P"+'</font>')

            master_list.append(usr_list)
    if t13 == 0:
       tt1 = 0
    else:
       tt1 = round((t12/t13)*100,2)
    total = ["<b>Total</b>","","",t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,round(t12/60,2),round(t13/60,2),tt1,'<font color="green">'+str(p)+'</font>'+"/"+'<font color="blue">'+str(hd)+'</font>'+"/"+'<font color="red">'+str(l)+'</font>']
    return master_list,total
def create_homepage_cost(users_list,date_range):
    master_list = []
    total = []
    t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13 = 0,0,0,0,0,0,0,0,0,0,0,0,0
    p,l,hd,wl = 0,0,0,0

    if not users_list=='ALL':
        for today_date in date_range:
            #print(today_date)
            usr_list = []
            prod_val = 0
            benchmark_var = 0

            usr_list.append('')
            usr_list.append('')
            usr_list.append(today_date.replace('-01','-JAN').replace('-02','-FEB').replace('-03','-MAR').replace('-04','-APR').replace('-05','-MAY').replace('-06','-JUN').replace('-07','-JUL').replace('-08','-AUG').replace('-09','-SEP').replace('-10','-OCT').replace('-11','-NOV').replace('-12','-DEC'))

            feas = productivity.objects.all().filter(timestamp__contains=today_date,task='Brand study',sub_task='Completed').count()
            feas_ob = productivity.objects.filter(timestamp__contains=today_date,task='Brand study',sub_task='Completed').aggregate(Sum('productivity'))
            productvty = feas_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t1+=feas 
            usr_list.append(feas)

            cr = productivity.objects.all().filter(timestamp__contains=today_date,task='Brand study validation',sub_task__startswith='Completed').count()
            cr_ob = productivity.objects.filter(timestamp__contains=today_date,task='Brand study validation',sub_task__startswith='Completed').aggregate(Sum('productivity'))
            productvty = cr_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t2+= cr
            usr_list.append(cr)

            cr_review = productivity.objects.all().filter(timestamp__contains=today_date,task='PTC',sub_task__startswith='Completed').count()
            cr_review_ob1 = productivity.objects.filter(timestamp__contains=today_date,task='PTC',sub_task__startswith='Completed').aggregate(Sum('productivity'))
            productvty = cr_review_ob1.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            
            else:
                prod_val += int(productvty)
                t3+= cr_review
            usr_list.append(cr_review)

            cr_review_ob2 = productivity.objects.filter(timestamp__contains=today_date,task='PTV',sub_task__startswith='Completed').count()
            crawl_ob2 = productivity.objects.all().filter(timestamp__contains=today_date,task='PTV',sub_task__startswith='Completed').aggregate(Sum('productivity'))
            productvty = crawl_ob2.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t4+= cr_review_ob2 
            usr_list.append(cr_review_ob2)

            crawl = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - DQ',sub_task='VV completed').count()
            crawl_ob = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - DQ',sub_task='VV completed').aggregate(Sum('productivity'))
            productvty = crawl_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t4+= crawl 
            usr_list.append(crawl)

            scrape = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - DQ',sub_task__startswith='BEM completed').count()
            scrape_ob = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - DQ',sub_task__startswith='BEM completed').aggregate(Sum('productivity'))
            productvty = scrape_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t5+= scrape 
            usr_list.append(scrape)

            reconf = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='Publised with ion file').count()
            reconf_ob = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='Publised with ion file').aggregate(Sum('productivity'))
            productvty = reconf_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t6+= reconf 
            usr_list.append(reconf)

            reconf_a = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='VV completed').count()
            reconf_a_ob = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='VV completed').aggregate(Sum('productivity'))
            productvty = reconf_a_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t7+= reconf_a
            usr_list.append(reconf_a)

            apprvd = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='BEM completed').count()
            apprvd_ob = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='BEM completed').aggregate(Sum('productivity'))
            productvty = apprvd_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t8+= apprvd 
            usr_list.append(apprvd)
            
            #aoa
            count_aoa= productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - DQ',sub_task__startswith='Published').count()
            aoa_ob = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - DQ',sub_task='Published').aggregate(Sum('productivity'))
            aoa = aoa_ob.get('productivity__sum')
            if aoa is None:
                prod_val += 0
            else:
                prod_val += int(aoa)
                t9+= count_aoa
            usr_list.append(count_aoa)

            #asins
            #asin_ob = productivity.objects.all().filter(timestamp__contains=today_date,task='',sub_task__startswith='asin').aggregate(Sum('task'))
            #asin = asin_ob.get('task__sum')
            #value_productivity = benchmark.objects.all().filter(task="Asin")
            #print(value_productivity)
            #if asin is None:
                #prod_val += 0
                #usr_list.append(0)
            #else:
                #prod_val += int(asin)*value_productivity.productivity
                #t10+= int(asin)
                #usr_list.append(int(asin))
            

            #adhoc
            adhoc_ob = productivity.objects.all().filter(timestamp__contains=today_date,brand='Adhoc').aggregate(Sum('productivity'))
            adhoc = adhoc_ob.get('productivity__sum')
            comp_ob = productivity.objects.all().filter(timestamp__contains=today_date,sub_task='Complexity Hours').aggregate(Sum('productivity'))
            comp = comp_ob.get('productivity__sum')
            
            master_list.append(usr_list)
    else:
        for today_date in date_range:
            usr_list = []
            prod_val = 0
            benchmark_var = 0

            usr_list.append('')
            usr_list.append('')
            usr_list.append(today_date.replace('-01','-JAN').replace('-02','-FEB').replace('-03','-MAR').replace('-04','-APR').replace('-05','-MAY').replace('-06','-JUN').replace('-07','-JUL').replace('-08','-AUG').replace('-09','-SEP').replace('-10','-OCT').replace('-11','-NOV').replace('-12','-DEC'))

            feas = productivity.objects.all().filter(timestamp__contains=today_date,task='Brand study',sub_task='Completed').count()
            feas_ob = productivity.objects.filter(timestamp__contains=today_date,task='Brand study',sub_task='Completed').aggregate(Sum('productivity'))
            productvty = feas_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t1+=feas 
            usr_list.append(feas)

            cr = productivity.objects.all().filter(timestamp__contains=today_date,task='Brand study validation',sub_task__startswith='Completed').count()
            cr_ob = productivity.objects.filter(timestamp__contains=today_date,task='Brand study validation',sub_task__startswith='Completed').aggregate(Sum('productivity'))
            productvty = cr_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t2+= cr
            usr_list.append(cr)

            cr_review = productivity.objects.all().filter(timestamp__contains=today_date,task='PTC',sub_task__startswith='Completed').count()
            cr_review_ob1 = productivity.objects.filter(timestamp__contains=today_date,task='PTC',sub_task__startswith='Completed').aggregate(Sum('productivity'))
            productvty = cr_review_ob1.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            
            else:
                prod_val += int(productvty)
                t3+= cr_review
            usr_list.append(cr_review)

            cr_review_ob2 = productivity.objects.filter(timestamp__contains=today_date,task='PTV',sub_task__startswith='Completed').count()
            crawl_ob2 = productivity.objects.all().filter(timestamp__contains=today_date,task='PTV',sub_task__startswith='Completed').aggregate(Sum('productivity'))
            productvty = crawl_ob2.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t4+= cr_review_ob2 
            usr_list.append(cr_review_ob2)

            crawl = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - DQ',sub_task='VV completed').count()
            crawl_ob = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - DQ',sub_task='VV completed').aggregate(Sum('productivity'))
            productvty = crawl_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t4+= crawl 
            usr_list.append(crawl)

            scrape = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - DQ',sub_task__startswith='BEM completed').count()
            scrape_ob = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - DQ',sub_task__startswith='BEM completed').aggregate(Sum('productivity'))
            productvty = scrape_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t5+= scrape 
            usr_list.append(scrape)

            reconf = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='Publised with ion file').count()
            reconf_ob = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='Publised with ion file').aggregate(Sum('productivity'))
            productvty = reconf_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t6+= reconf 
            usr_list.append(reconf)

            reconf_a = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='VV completed').count()
            reconf_a_ob = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='VV completed').aggregate(Sum('productivity'))
            productvty = reconf_a_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t7+= reconf_a
            usr_list.append(reconf_a)

            apprvd = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='BEM completed').count()
            apprvd_ob = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - Manual',sub_task__startswith='BEM completed').aggregate(Sum('productivity'))
            productvty = apprvd_ob.get('productivity__sum')
            if productvty is None:
                prod_val += 0
            else:
                prod_val += int(productvty)
                t8+= apprvd 
            usr_list.append(apprvd)
            
            #aoa
            count_aoa= productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - DQ',sub_task__startswith='Published').count()
            aoa_ob = productivity.objects.all().filter(timestamp__contains=today_date,task='Backfill - DQ',sub_task='Published').aggregate(Sum('productivity'))
            aoa = aoa_ob.get('productivity__sum')
            if aoa is None:
                prod_val += 0
            else:
                prod_val += int(aoa)
                t9+= count_aoa
            usr_list.append(count_aoa)

            #asins
            #asin_ob = productivity.objects.all().filter(timestamp__contains=today_date,task='',sub_task__startswith='asin').aggregate(Sum('task'))
            #asin = asin_ob.get('task__sum')
            #value_productivity = benchmark.objects.all().filter(task="Asin")
            #print(value_productivity)
            #if asin is None:
                #prod_val += 0
                #usr_list.append(0)
            #else:
                #prod_val += int(asin)*value_productivity.productivity
                #t10+= int(asin)
                #usr_list.append(int(asin))
            

            #adhoc
            adhoc_ob = productivity.objects.all().filter(timestamp__contains=today_date,brand='Adhoc').aggregate(Sum('productivity'))
            adhoc = adhoc_ob.get('productivity__sum')
            comp_ob = productivity.objects.all().filter(timestamp__contains=today_date,sub_task='Complexity Hours').aggregate(Sum('productivity'))
            comp = comp_ob.get('productivity__sum')
            
            master_list.append(usr_list)
    
    total = ["<b>Total</b>","","",t1,t2,t3,t4,t5,t6,t7,t8,t9,'<font color="green">'+str(p)+'</font>'+"/"+'<font color="blue">'+str(hd)+'</font>'+"/"+'<font color="red">'+str(l)+'</font>']
    return master_list,total
def monthly_cost(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    usr_list = get_rda()

    if not ob:
        return redirect('login')

    elif role_ob.user_role != "manager":
        return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        for i in get_auditor():
            usr_list.append(i)
        usr_list.sort()

        Month = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        mon  = [1,2,3,4,5,6,7,8,9,10,11,12]
    
        ben = []
        for r in usr_list:
            u = []
            u.append(r)
            for i in mon:   
                benchmark_ob = productivity.objects.all().filter(brand="Login",user=r,timestamp__month=i).aggregate(Sum('productivity'))
                bench = benchmark_ob.get('productivity__sum')
                #print(bench)
                prod_ob = productivity.objects.all().filter(user=r,timestamp__month=i).exclude(brand="Login").aggregate(Sum('productivity'))
                prod = prod_ob.get('productivity__sum')
                #print(prod)
                if bench==None or prod==None:
                    percent = 0
                else:
                    percent = (prod/bench)*100
                u.append('<font color="blue">'+str(round(percent,2))+'</font>')
                qual_ob = productivity.objects.all().filter(brand="Quality",user=r,phase=str(Month[i-1])+str(datetime.today().year)).first()
                if qual_ob is None:
                    u.append('0')
                else:
                    ob = productivity.objects.get(brand="Quality",user=r,phase=str(Month[i-1])+str(datetime.today().year))
                    u.append('<font color="green">'+str(round(float(ob.ask),2))+'</font>')
            ben.append(u)
        return render(request,'smt_smpo_dashboard/month.html',{'user':user,'role':get_role(user),'ben':ben,'MONTH':Month,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)})

def productivity_edit(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')

    elif role_ob.user_role != "manager":
        return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        prompt = {'user':user,'role':get_role(user),
            'order' : 'Order of xlsx should be pid , Revised productivity in minutes','sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)
        }
        if request.method == 'GET':
            return render(request, 'smt_smpo_dashboard/edit_prod.html', prompt)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        for x in a:
            DB2=productivity.objects.get(pid=str(x[0]))
            DB2.productivity = str(x[1])
            DB2.save()

        context= {'user':user,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
        return render(request,'smt_smpo_dashboard/edit_prod.html',context)

def prod_edit(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')

    elif role_ob.user_role != "manager":
        return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        prompt = {'user':user,'role':get_role(user),
            'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)
        }
        if request.method == 'GET':
            return render(request, 'smt_smpo_dashboard/prod_edit.html', prompt)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        for x in a:
            #print('hilo')
            #print(int(x[0]))
            DB2=productivity.objects.get(pid=int(x[0]))
            if(DB2):
                if not(pd.isnull(x[1])):
                    DB2.website=str(x[1])
                if not(pd.isnull(x[2])):
                    DB2.ec_partition_id=str(x[2])
                if not(pd.isnull(x[3])):
                    DB2.brand=str(x[3])
                if not(pd.isnull(x[4])):
                    DB2.brand_iteration=str(x[4])
                if not(pd.isnull(x[5])):
                    DB2.phase=str(x[5])
                if not(pd.isnull(x[6])):
                    DB2.user=str(x[6])
                if not(pd.isnull(x[7])):
                    DB2.task=str(x[7])
                if not(pd.isnull(x[8])):
                    DB2.sub_task=str(x[8])
                if not(pd.isnull(x[9])):
                    DB2.productivity=str(x[9])

                DB2.save()

        context= {'user':user,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
        return render(request,'smt_smpo_dashboard/prod_edit.html',context)

                
def brand_ops_edit(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')

    elif role_ob.user_role != "manager":
        return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        prompt = {'user':user,'role':get_role(user),
            'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)
        }
        if request.method == 'GET':
            return render(request, 'smt_smpo_dashboard/brand_ops_edit.html', prompt)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        for x in a:
            #print('hilo')
            #print(int(x[0]))
            DB2=brand_ops.objects.get(bid=int(x[0]))
            if(DB2):

                if not(pd.isnull(x[1])):
                    DB2.brand=str(x[1])
                if not(pd.isnull(x[2])):
                    DB2.website=str(x[2])
                if not(pd.isnull(x[3])):
                    DB2.ec_partition_id=str(x[3])
                if not(pd.isnull(x[4])):
                    DB2.ssl_completed_date=str(x[4])
                if not(pd.isnull(x[5])):
                    DB2.matching_completed_date=str(x[5])
                if not(pd.isnull(x[6])):
                    DB2.incremental_matching_completed_date=str(x[6])
                if not(pd.isnull(x[7])):
                    DB2.bs_owner=str(x[7])
                if not(pd.isnull(x[8])):
                    DB2.bs_status=str(x[8])
                if not(pd.isnull(x[9])):
                    DB2.bs_allocation_date=str(x[9])
                if not(pd.isnull(x[10])):
                    DB2.bs_completion_date=str(x[10])
                if not(pd.isnull(x[11])):
                    DB2.bsv_owner=str(x[11])
                if not(pd.isnull(x[12])):
                    DB2.bsv_status=str(x[12])
                if not(pd.isnull(x[13])):
                    DB2.bsv_allocation_date=str(x[13])
                if not(pd.isnull(x[14])):
                    DB2.bsv_completion_date=str(x[14])
                if not(pd.isnull(x[15])):
                    DB2.ptc_owner=str(x[15])
                if not(pd.isnull(x[16])):
                    DB2.ptc_status=str(x[16])
                if not(pd.isnull(x[17])):
                    DB2.ptc_allocation_date=str(x[17])
                if not(pd.isnull(x[18])):
                    DB2.ptc_completion_date=str(x[18])
                if not(pd.isnull(x[19])):
                    DB2.ptv_owner=str(x[19])
                if not(pd.isnull(x[20])):
                    DB2.ptv_status=str(x[20])
                if not(pd.isnull(x[21])):
                    DB2.ptv_allocation_date=str(x[21])
                if not(pd.isnull(x[22])):
                    DB2.ptv_completion_date=str(x[22])
                if not(pd.isnull(x[23])):
                    DB2.backfill_owner=str(x[23])
                if not(pd.isnull(x[24])):
                    DB2.backfill_status=str(x[24])
                if not(pd.isnull(x[25])):
                    DB2.backfill_allocation_date=str(x[25])
                if not(pd.isnull(x[26])):
                    DB2.backfill_completion_date=str(x[26])
                if not(pd.isnull(x[27])):
                    DB2.bem_owner=str(x[27])
                if not(pd.isnull(x[28])):
                    DB2.bem_status=str(x[28])
                if not(pd.isnull(x[29])):
                    DB2.bem_completion_date=str(x[29])
                if not(pd.isnull(x[30])):
                    DB2.bem_allocation_date=str(x[30])
                if not(pd.isnull(x[31])):
                    DB2.published_owner=str(x[31])
                if not(pd.isnull(x[32])):
                    DB2.published_status=str(x[32])
                if not(pd.isnull(x[33])):
                    DB2.published_allocation_date=str(x[33])
                if not(pd.isnull(x[34])):
                    DB2.published_completion_date=str(x[34])
                if not(pd.isnull(x[35])):
                    DB2.backfill_type=str(x[35])
                if not(pd.isnull(x[36])):
                    DB2.language=str(x[36])
                if not(pd.isnull(x[37])):
                    DB2.business_request=str(x[37])
                if not(pd.isnull(x[38])):
                    DB2.brand_iteration=str(x[38])
                if not(pd.isnull(x[39])):
                    DB2.bs_priority=str(x[39])
                if not(pd.isnull(x[40])):
                    DB2.pt_request_count=str(x[40])
                if not(pd.isnull(x[41])):
                    DB2.bs_ptname=str(x[41])
                if not(pd.isnull(x[42])):
                    DB2.bs_attributes_count=str(x[42])
                if not(pd.isnull(x[43])):
                    DB2.bs_comments=str(x[43])
                if not(pd.isnull(x[44])):
                    DB2.bs_filename=str(x[44])
                if not(pd.isnull(x[45])):
                    DB2.bs_path=str(x[45])
                if not(pd.isnull(x[46])):
                    DB2.pt_not_found=str(x[46])
                if not(pd.isnull(x[47])):
                    DB2.bsv_pt_not_found=str(x[47])
                if not(pd.isnull(x[48])):
                    DB2.bsv_attributes_count=str(x[48])
                if not(pd.isnull(x[49])):
                    DB2.bsv_comments=str(x[49])
                if not(pd.isnull(x[50])):
                    DB2.bsv_inaccurate_selection=str(x[50])
                if not(pd.isnull(x[51])):
                    DB2.bsv_sample_selection=str(x[51])
                if not(pd.isnull(x[52])):
                    DB2.ptc_selection_size=str(x[52])
                if not(pd.isnull(x[53])):
                    DB2.parent_count=str(x[53])
                if not(pd.isnull(x[54])):
                    DB2.bundle_count=str(x[54])
                if not(pd.isnull(x[55])):
                    DB2.ptc_comments=str(x[55])
                if not(pd.isnull(x[56])):
                    DB2.ptc_file_name=str(x[56])
                if not(pd.isnull(x[57])):
                    DB2.ptc_path=str(x[57])
                if not(pd.isnull(x[58])):
                    DB2.ptv_selection_size=str(x[58])
                if not(pd.isnull(x[59])):
                    DB2.ptv_comments=str(x[59])
                if not(pd.isnull(x[60])):
                    DB2.ptv_file_name=str(x[60])
                if not(pd.isnull(x[61])):
                    DB2.ptv_inaccurate_selection=str(x[61])
                if not(pd.isnull(x[62])):
                    DB2.ptv_sample_selection=str(x[62])
                if not(pd.isnull(x[63])):
                    DB2.backfill_pt_count=str(x[63])
                if not(pd.isnull(x[64])):
                    DB2.backfill_source_attributes_count=str(x[64])
                if not(pd.isnull(x[65])):
                    DB2.backfill_pt_source_attributes_count=str(x[65])
                if not(pd.isnull(x[66])):
                    DB2.backfill_comments=str(x[66])
                if not(pd.isnull(x[67])):
                    DB2.bem_attempted=str(x[67])
                #if not(pd.isnull(x[68])):
                    #DB2.bem_converted=str(x[68])
                if not(pd.isnull(x[69])):
                    DB2.validation_inaccurate_selection=str(x[69])
                if not(pd.isnull(x[70])):
                    DB2.validation_sample_selection=str(x[70])
                if not(pd.isnull(x[71])):
                    DB2.require_ontology_attributes_prior_count=str(x[71])
                if not(pd.isnull(x[72])):
                    DB2.converted_ontology_count=str(x[72])
                if not(pd.isnull(x[73])):
                    DB2.require_ontology_attributes_post_count=str(x[73])
                if not(pd.isnull(x[74])):
                    DB2.slots_backfilled_count=str(x[74])
                if not(pd.isnull(x[75])):
                    DB2.bem_publish_comment=str(x[75])

                DB2.save()

        context= {'user':user,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
        return render(request,'smt_smpo_dashboard/brand_ops_edit.html',context)

def brand_prog_edit(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')

    elif role_ob.user_role != "manager":
        return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        prompt = {'user':user,'role':get_role(user),
            'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)
        }
        if request.method == 'GET':
            return render(request, 'smt_smpo_dashboard/brand_prog_edit.html', prompt)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        #brand_cols=['bid','brand','website','first_level_ssp_status','program_usecase','scrape_ssp_status','uec_reflection_status','mkpl','is_backfill','ssl_auto_kvp_status','identity_dp_backfill_status','is_brand_with_identity_dp','matching_status','matching_model','is_incremental_matching','ec_gv_matching_cvg_gt_20','ptc_status','non_criteria_status','priority','overall_website_status','ds_queue','backfill_status','detailed_backfill_status','nm_status','is_bem','is_bem_converted','is_bem_attempted','brand_status','business_usecase','backfill_business_usecase','tt_comments','backfill_type','language','business_request','brand_iteration','matching_start_date','date','mp_id','keys_available_website_count','keys_count','keys_count_gt_20','slots_backfilled_count','idf_av_performance','idf_av_ssl_performance','scrape_metric','matching_gv_coverage','matching_sku_coverage','incremental_matching_gv_coverage','incremental_sku_coverage','website_id']
        for x in a:
            DB2=brand_program.objects.get(bid=int(x[0]))
            #c='DB2.'+str(brand_cols[3])
            #c='6'
            #DB2.scrape_ssp_status='8'
            #DB2.save()
            #print(DB2)
            i=0
            if(DB2):
                if not(pd.isnull(x[1])):
                    DB2.brand=str(x[1])
                if not(pd.isnull(x[2])):
                    DB2.website=str(x[2])
                if not(pd.isnull(x[3])):
                    DB2.first_level_ssp_status=str(x[3])
                if not(pd.isnull(x[4])):
                    DB2.program_usecase=str(x[4])
                if not(pd.isnull(x[5])):
                    DB2.scrape_ssp_status=str(x[5])
                if not(pd.isnull(x[6])):
                    DB2.uec_reflection_status=str(x[6])
                if not(pd.isnull(x[7])):
                    DB2.mkpl=str(x[7])
                if not(pd.isnull(x[8])):
                    DB2.is_backfill=str(x[8])
                if not(pd.isnull(x[9])):
                    DB2.ssl_auto_kvp_status=str(x[9])
                if not(pd.isnull(x[10])):
                    DB2.identity_dp_backfill_status=str(x[10])
                if not(pd.isnull(x[11])):
                    DB2.is_brand_with_identity_dp=str(x[11])
                if not(pd.isnull(x[12])):
                    DB2.matching_status=str(x[12])
                if not(pd.isnull(x[13])):
                    DB2.matching_model=str(x[13])
                if not(pd.isnull(x[14])):
                    DB2.is_incremental_matching=str(x[14])
                if not(pd.isnull(x[15])):
                    DB2.ec_gv_matching_cvg_gt_20=str(x[15])
                if not(pd.isnull(x[16])):
                    DB2.ptc_status=str(x[16])
                if not(pd.isnull(x[17])):
                    DB2.non_criteria_status=str(x[17])
                if not(pd.isnull(x[18])):
                    DB2.priority=str(x[18])
                if not(pd.isnull(x[19])):
                    DB2.overall_website_status=str(x[19])
                    DB2.flag_overall_website_status='f1'
                if not(pd.isnull(x[20])):
                    DB2.ds_queue=str(x[20])
                if not(pd.isnull(x[21])):
                    DB2.backfill_status=str(x[21])
                if not(pd.isnull(x[22])):
                    DB2.detailed_backfill_status=str(x[22])
                if not(pd.isnull(x[23])):
                    DB2.nm_status=str(x[23])
                if not(pd.isnull(x[24])):
                    DB2.is_bem=str(x[24])
                #if not(pd.isnull(x[25])):
                    #DB2.is_bem_converted=str(x[25])
                #if not(pd.isnull(x[26])):
                    #DB2.is_bem_attempted=str(x[26])
                if not(pd.isnull(x[27])):
                    DB2.brand_status=str(x[27])
                if not(pd.isnull(x[28])):
                    DB2.business_usecase=str(x[28])
                if not(pd.isnull(x[29])):
                    DB2.backfill_business_usecase=str(x[29])
                if not(pd.isnull(x[30])):
                    DB2.tt_comments=str(x[30])
                if not(pd.isnull(x[31])):
                    DB2.backfill_type=str(x[31])
                if not(pd.isnull(x[32])):
                    DB2.language=str(x[32])
                if not(pd.isnull(x[33])):
                    DB2.business_request=str(x[33])
                if not(pd.isnull(x[34])):
                    DB2.brand_iteration=str(x[34])
                if not(pd.isnull(x[35])):
                    DB2.matching_start_date=str(x[35])
                if not(pd.isnull(x[36])):
                    DB2.date=str(x[36])
                if not(pd.isnull(x[37])):
                    DB2.mp_id=str(x[37])
                if not(pd.isnull(x[38])):
                    DB2.keys_available_website_count=str(x[38])
                if not(pd.isnull(x[39])):
                    DB2.keys_count=str(x[39])
                if not(pd.isnull(x[40])):
                    DB2.keys_count_gt_20=str(x[40])
                if not(pd.isnull(x[41])):
                    DB2.slots_backfilled_count=str(x[41])
                if not(pd.isnull(x[42])):
                    DB2.idf_av_performance=str(x[42])
                if not(pd.isnull(x[43])):
                    DB2.idf_av_ssl_performance=str(x[43])
                if not(pd.isnull(x[44])):
                    DB2.scrape_metric=str(x[44])
                if not(pd.isnull(x[45])):
                    DB2.matching_gv_coverage=str(x[45])
                if not(pd.isnull(x[46])):
                    DB2.matching_sku_coverage=str(x[46])
                if not(pd.isnull(x[47])):
                    DB2.incremental_matching_gv_coverage=str(x[47])
                if not(pd.isnull(x[48])):
                    DB2.incremental_sku_coverage=str(x[48])
                if not(pd.isnull(x[49])):
                    DB2.website_id=str(x[49])

                DB2.save()

        context= {'user':user,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
        return render(request,'smt_smpo_dashboard/brand_prog_edit.html',context)

def benchmark_edit(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')

    elif role_ob.user_role != "manager":
        return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        prompt = {'user':user,'role':get_role(user),
            'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)
        }
        if request.method == 'GET':
            return render(request, 'smt_smpo_dashboard/benchmark_edit.html', prompt)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        #brand_cols=['bid','brand','website','first_level_ssp_status','program_usecase','scrape_ssp_status','uec_reflection_status','mkpl','is_backfill','ssl_auto_kvp_status','identity_dp_backfill_status','is_brand_with_identity_dp','matching_status','matching_model','is_incremental_matching','ec_gv_matching_cvg_gt_20','ptc_status','non_criteria_status','priority','overall_website_status','ds_queue','backfill_status','detailed_backfill_status','nm_status','is_bem','is_bem_converted','is_bem_attempted','brand_status','business_usecase','backfill_business_usecase','tt_comments','backfill_type','language','business_request','brand_iteration','matching_start_date','date','mp_id','keys_available_website_count','keys_count','keys_count_gt_20','slots_backfilled_count','idf_av_performance','idf_av_ssl_performance','scrape_metric','matching_gv_coverage','matching_sku_coverage','incremental_matching_gv_coverage','incremental_sku_coverage','website_id']
        for x in a:
            DB2=benchmark.objects.get(tid=int(x[0]))
            if(DB2):
                if not(pd.isnull(x[1])):
                    DB2.role=str(x[1])
                if not(pd.isnull(x[2])):
                    DB2.task=str(x[2])
                if not(pd.isnull(x[3])):
                    DB2.subtask=str(x[3])
                if not(pd.isnull(x[4])):
                    DB2.lower_select=str(x[4])
                if not(pd.isnull(x[5])):
                    DB2.higher_select=str(x[5])
                if not(pd.isnull(x[6])):
                    DB2.lower_pt=str(x[6])
                if not(pd.isnull(x[7])):
                    DB2.higher_pt=str(x[7])
                if not(pd.isnull(x[8])):
                    DB2.iterations=str(x[8])
                if not(pd.isnull(x[9])):
                    DB2.productivity=str(x[9])
                if not(pd.isnull(x[10])):
                    DB2.complexity=str(x[10])
                if not(pd.isnull(x[11])):
                    DB2.parameter=str(x[11])

                DB2.save()
        
        context= {'user':user,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
        return render(request,'smt_smpo_dashboard/brand_prog_edit.html',context)

def producitvity_table(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')

    elif role_ob.user_role != "manager":
        return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        template = 'smt_smpo_dashboard/prod_db.html'

        associate = get_rda()
        for i in get_auditor():
            associate.append(i)
        associate.sort()

        qs = productivity.objects.all()

        brand = request.GET.get('brand')
        brand_iteration = request.GET.get('brand_iteration')
        ec_partition_id = request.GET.get('ec_partition_id')
        phase = request.GET.get('phase')
        rda = request.GET.get('rda')
        stat = request.GET.get('stat')
        etadate_min = request.GET.get('date_min')
        etadate_max = request.GET.get('date_max')

        if brand:
            qs = qs.filter(brand__icontains=brand)

        if brand_iteration:
            qs = qs.filter(brand_iteration__icontains=brand_iteration)

        if ec_partition_id:
            qs = qs.filter(ec_partition_id__icontains=ec_partition_id)
    
        if phase and phase != 'Choose...':
            qs = qs.filter(phase=phase)

        if rda and rda != 'Choose...':
            qs = qs.filter(user=rda)
    
        if stat and stat != 'Choose...':
            qs = qs.filter(sub_task=stat)

        if etadate_min:
            qs = qs.filter(timestamp__gte=etadate_min)

        if etadate_max:
            qs = qs.filter(timestamp__lte=etadate_max)
    
        if request.POST:
            if str(request.POST.get('form_type'))=="del":
                ob = productivity.objects.filter(pid=str(request.POST.get('id'))).delete()
                return redirect('producitvity_table')
            else:
                df_output = pd.DataFrame(list(qs.values())) 
                excel_file = IO()
                xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
                df_output.to_excel(xlwriter, 'sheetname')

                xlwriter.save()
                xlwriter.close()
                excel_file.seek(0)
                response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename=myfile.xlsx'
                return response
 
        context = {'RDA':associate, 'PHASE':create_phase(),'object':qs.all().order_by("-timestamp")[:20],'stat':set(get_status())}
        return render(request,template,context)
def main_prod(request):
    current_user = request.user
    user = current_user.username
    
    date_range = []
    delta = timedelta(days=1)

    start_date=datetime.today()
    start_date = start_date.replace(day=1)
    end_date=datetime.today()
        
    while start_date <= end_date:
        date_range.append(start_date.strftime("%Y-%m-%d"))   
        start_date += delta

    master_list,total = create_cost([user],date_range)

    if request.POST:
        start_date=request.POST.get('startDate')
        start_date= datetime.strptime(start_date,'%Y-%m-%d')
        end_date=request.POST.get('endDate')
        end_date= datetime.strptime(end_date,'%Y-%m-%d')
        date_range1 = []
        while start_date <= end_date:
            date_range1.append(start_date.strftime("%Y-%m-%d"))  
            start_date += delta
        master_list1,total1 = create_cost([user],date_range1)
        context1 = {'user':user,'role':get_role(user),'master_list':master_list1,'total':total1}
        return render(request,'smt_smpo_dashboard/main_prod.html',context1)
            
    context = {'user':user,'role':get_role(user),'master_list':master_list,'total':total}
    return render(request,'smt_smpo_dashboard/main_prod.html',context)

def crawl_r(request):
    current_user = request.user
    user = current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')

    elif role_ob.special_role1 != "lead":
        return HttpResponse("<h1>You are not an authorized person!</h1>")
    else:
        obj = brand_ops.objects.all().filter(backfill_status__contains='ompleted').exclude(published_status__contains='ompleted') 

        report = []
        for i in obj:
            u = []
            obc = productivity.objects.all().filter(brand=i.brand,website=i.website,user=i.published_owner,sub_task__contains='ompleted').count()
            if obc==1:
                dt = productivity.objects.get(brand=i.brand,website=i.website,user=i.published_owner,sub_task__contains='ompleted')
                u.append(i.brand)
                u.append(i.website)
                u.append(i.published_owner)
                u.append(i.backfill_status)
                date = dt.timestamp.date()
                u.append(date)
                today = datetime.today()
                date1 = datetime.strftime(dt.timestamp, "%d-%m-%Y")
                date2 = datetime.strftime(today, "%d-%m-%Y")
                date1 = pd.to_datetime(date1,format="%d-%m-%Y").date()
                date2 = pd.to_datetime(date2,format="%d-%m-%Y").date()
                days = date2 - date1
                u.append(str(days).split(',')[0])
                report.append(u)

            else:
               
                #report.append(u)
                
                u=[]

        context = {'report':report,'user':user}
        return render(request,'smt_smpo_dashboard/crawl_report.html',context)
def lead(request):
    current_user = request.user
    user = current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')

    elif role_ob.special_role1 == "None":
        if role_ob.user_role == "auditor":
            return redirect('auditor')
        elif role_ob.user_role == "rda":
            return redirect('rda')
    else:
        return render(request,'smt_smpo_dashboard/lead.html',{'user':user})

def core(request):
    current_user = request.user
    user = current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')

    elif role_ob.special_role1 == "":
        if role_ob.user_role == "auditor":
            return redirect('auditor')
        elif role_ob.user_role == "sme":
            return redirect('sme')
    else:
    	print('hi')
    	return render(request,'smt_smpo_dashboard/core.html',{'user':user,'sp_role':role_ob.special_role1})


def aud_cost(request):

    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    date_range = []
    delta = timedelta(days=1)

    start_date=datetime.today()
    start_date = start_date.replace(day=1)
    end_date=datetime.today()
        
    while start_date <= end_date:
        date_range.append(start_date.strftime("%Y-%m-%d"))   
        start_date += delta

    master_list,total = create_cost([user],date_range)

    if request.POST:
        start_date=request.POST.get('startDate')
        start_date= datetime.strptime(start_date,'%Y-%m-%d')
        end_date=request.POST.get('endDate')
        end_date= datetime.strptime(end_date,'%Y-%m-%d')
        date_range1 = []
        while start_date <= end_date:
            date_range1.append(start_date.strftime("%Y-%m-%d"))  
            start_date += delta
        master_list1,total1 = create_cost([user],date_range1)
        context1 = {'user':user,'role':get_role(user),'master_list':master_list1,'total':total1,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
        return render(request,'smt_smpo_dashboard/audit_cost.html',context1)
            
    context = {'user':user,'role':get_role(user),'master_list':master_list,'total':total,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
    return render(request,'smt_smpo_dashboard/audit_cost.html',context) 

def sme_cost(request):

    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    usr_list = []
    #usr_qry=profile.objects.all().filter(user_name=user)
    usr_list.append(user)
    print(usr_list)
    if not ob:
        return redirect('login')

    else:
        #for i in get_auditor():
            #usr_list.append(i)
        today = datetime.today()
        master_list,tot = create_cost(usr_list,[today.strftime("%Y-%m-%d")])

        if request.POST:
            dt=request.POST.get('startDate')
            date = datetime.strptime(dt,'%Y-%m-%d')
            master_list,tot = create_cost(usr_list,[datetime.strftime(date,'%Y-%m-%d')])
            context1 = {'role':get_role(user),'user':user,'master_list':master_list,'today_date':datetime.strptime(dt,'%Y-%m-%d')}
            return render(request,'smt_smpo_dashboard/sme_cost.html',context1) 

        context = {'role':get_role(user),'user':user,'master_list':master_list,'today_date':datetime.today()}
        return render(request,'smt_smpo_dashboard/sme_cost.html',context) 

'''def eod_summary(request):

    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)'''

def eod_summary(request):

    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    usr_list = []

    for ob in profile.objects.all().exclude(user_role="manager"):
        usr_list.append(ob.user_name)
    
    #usr_qry=profile.objects.all().filter(user_name=user)
    #usr_list.append(user)
    #print(usr_list)
    if not ob:
        return redirect('login')

    else:
        #for i in get_auditor():
            #usr_list.append(i)
        today = datetime.today()
        master_list2,tot = create_cost(usr_list,[today.strftime("%Y-%m-%d")])
        #print(master_list2[18])
        #master_list=[[l[:14]] for l in master_list2]
        master_list=[]
        for l in master_list2:
            #print([l[17:]])
            master_list.append([l[:14]]+[l[17:]])
            #master_list.append([l[17:]])
            #master_list.append(l[1])
            #master_list.append(l[2])
            #master_list.append(l[17])
        #print(master_list)
        if request.POST:
            dt=request.POST.get('startDate')
            date = datetime.strptime(dt,'%Y-%m-%d')
            master_list2,tot = create_cost(usr_list,[datetime.strftime(date,'%Y-%m-%d')])
            #master_list=[[l[:14]] for l in master_list]
            master_list=[]
            for l in master_list2:
            #print([l[17:]])
                master_list.append([l[:14]]+[l[17:]])
            context1 = {'role':get_role(user),'user':user,'master_list':master_list,'today_date':datetime.strptime(dt,'%Y-%m-%d')}
            return render(request,'smt_smpo_dashboard/eod_summary.html',context1) 

        context = {'role':get_role(user),'user':user,'master_list':master_list,'today_date':datetime.today()}
        return render(request,'smt_smpo_dashboard/eod_summary.html',context) 

def sod_summary(request):

    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    usr_list = []

    for ob in profile.objects.all().exclude(user_role="manager"):
        usr_list.append(ob.user_name)
    
    #usr_qry=profile.objects.all().filter(user_name=user)
    #usr_list.append(user)
    #print(usr_list)
    if not ob:
        return redirect('login')

    else:
        #for i in get_auditor():
            #usr_list.append(i)
        today = datetime.today()
        master_list2,tot = sod_cost(usr_list,[today.strftime("%Y-%m-%d")])
        #print(master_list2[18])
        #master_list=[[l[:14]] for l in master_list2]
        master_list=[]
        for l in master_list2:
            #print([l[17:]])
            master_list.append([l[:14]]+[l[17:]])
            #master_list.append([l[17:]])
            #master_list.append(l[1])
            #master_list.append(l[2])
            #master_list.append(l[17])
        #print(master_list)
        

        context = {'role':get_role(user),'user':user,'master_list':master_list,'today_date':datetime.today()}
        return render(request,'smt_smpo_dashboard/sod_summary.html',context) 

def allocate_wb(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    #print(role_ob.column_names)
    if not ob:
        return redirect('login')
    elif not(role_ob.special_role2 == "master"): 
    	return redirect('master')
    else:
        template='smt_smpo_dashboard/website_upload.html'
        #print('hi')
        #print(str(request.POST.get('form-group')))

        if str(request.POST.get('form-group'))=="template":
        	col1='Brand'
        	col2='Website'
        	col3='Program /Use-case'
        	col4='MKPL'
        	col5='MP id'
        	col6='Language'
        	col7='Business request'
        	col8='Brand iteration'
        	col9='ec_partition_id(website_id)'
        	et=export_template(col1,col2,col3,col4,col5,col6,col7,col8,col9)
        	#print(et)
        	return et
        else:
            if request.method == 'GET':
                return render(request, template)

            XLX_FILE = request.FILES['file_name']
            df = pd.read_excel(XLX_FILE)
            a = df.values.tolist()
        	#print(a)
            error_list = []
            for x in a:
                #print(len(x))
                chk=0
                for i in range(len(x)):

                    if (pd.isnull(x[i])):
                        error_list.append('Brand row "'+str(x[0])+'" has empty column '+str(i))
                        chk+=1
                if(chk==0):
                    db1= brand_program.objects.filter(brand=str(x[0]),mp_id=str(x[4]),brand_iteration=str(x[7]))
                    if db1:
                    

                        dbd=brand_program.objects.get(brand=str(x[0]),mp_id=str(x[4]),brand_iteration=str(x[7]))
                    #print(dbd.website_id)
                        if (dbd.website_id=='TBD'):
                            error_list.append('update website id')
                        else:
                            error_list.append('brand already exists, should we re-process?')
                    else:
                        DB2=brand_program.objects.create(brand=str(x[0]),website=str(x[1]),program_usecase=str(x[2]),mkpl=str(x[3]),mp_id=str(x[4]),language=str(x[5]),business_request=str(x[6]),brand_iteration=str(x[7]),website_id=str(x[8]))
                        DB2.save()
            #print(error_list)
            context= {'user':user,'error':error_list}
            return render(request,template,context)

        '''if request.method == 'GET':
        	return render(request, template)
        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()

        error_list = []
        for x in a:
        	db1= brand_program.objects.filter(brand=str(x[0]))
        	if not db1:
        		DB2=brand_program.objects.create(brand=str(x[0]),website=str(x[1]),program_usecase=str(x[2]),mkpl=str(x[3]),mp_id=str(x[4]),language=str(x[5]),business_request=str(x[6]),brand_iteration=str(x[7]),website_id=str(x[8]))
        		DB2.save()
        	else:
        		error_list.append(db1)
        context= {'user':user,'error':error_list}
        return render(request,template,context)'''
def allocate_wb2(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')
    elif not(role_ob.special_role2 == "master"): 
        return redirect('master')
    else:
        template='smt_smpo_dashboard/ingest_bs.html'
        #print('hi')
        #print(str(request.POST.get('form-group')))

        if str(request.POST.get('form-group'))=="template":
            col1='Brand'
            col2='Website'
            col3='Program /Use-case'
            col4='MKPL'
            col5='MP id'
            col6='Language'
            col7='Business request'
            col8='Brand iteration'
            col9='ec_partition_id(website_id)'
            et=export_template(col1,col2,col3,col4,col5,col6,col7,col8,col9)
            #print(et)
            return et
        else:
            if request.method == 'GET':
                return render(request, template)

            XLX_FILE = request.FILES['file_name']
            df = pd.read_excel(XLX_FILE)
            a = df.values.tolist()
            #print(a)
            error_list = []
            for x in a:
                chk=0
                for i in range(len(x)):

                    if (pd.isnull(x[i])):
                        error_list.append('Brand row '+str(x[0])+'has empty column '+i)
                        chk+=1
                if(chk==0):
                    db1= brand_program.objects.filter(brand=str(x[0]),mp_id=str(x[4]),brand_iteration=str(x[7]))
                    if db1:
                        error_list.append('Brand'+str(x[0])+ 'Exists')
                    else:
                        DB2=brand_program.objects.create(brand=str(x[0]),website=str(x[1]),program_usecase=str(x[2]),mkpl=str(x[3]),mp_id=str(x[4]),language=str(x[5]),business_request=str(x[6]),brand_iteration=str(x[7]),website_id=str(x[8]))
                        DB2.save()
                

            context= {'user':user,'error':error_list}
            return render(request,template,context)
def update_wid(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')
    elif not(role_ob.special_role2 == "master"): 
        return redirect('master')

    else:
        template='smt_smpo_dashboard/update_wid.html'
        #prompt = {'order' : 'Order of xlsx should be rda, website, product_type , brand , allocated_month , phase' }
        
        if str(request.POST.get('form-group'))=="template":
            query_chk=brand_program.objects.filter(website_id='TBD')
            #print(query_chk[0].incremental_sku_coverage)
            if query_chk:
                col1='bid'
                col2='Brand'
                col3='Website'
                col4='ec_partition_id(website_id)'

                df_output = pd.DataFrame(columns=[col1,col2,col3,col4]) 
                for row in range(len(query_chk)):

                    df_output.loc[row,'bid']=query_chk[row].bid
                    df_output.loc[row,'Brand']=query_chk[row].brand
                    df_output.loc[row,'Website']=query_chk[row].website
            #et=export_template(col1,col2,col3,col4,col5,col6,col7,col8,col9)
            #print(et)
            else:
                df_output = pd.DataFrame(columns=['No Data matching the conditions'])
            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df_output.to_excel(xlwriter, 'sheetname',index=False)
            xlwriter.save()
            xlwriter.close()
            excel_file.seek(0)
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=template.xlsx'
            return response
        if request.method == 'GET':
            return render(request, template)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        #print(a)
        error_list = []
        for x in a:
            chk=0
            for i in range(len(x)):

                if (pd.isnull(x[i])):
                    error_list.append('Row with BID '+str(x[0])+'has empty values')
                    chk+=1
            if(chk==0):
                db1= brand_program.objects.filter(bid=int(x[0]))
                if db1:
                    db1= brand_program.objects.get(bid=int(x[0]))
                    db1.website_id=str(x[3])
                    try:
                        #print(db1)
                        db1.save()
                    except Exception as e:
                        error_list.append(e)
                else:
                    error_list.append(db1)
            
        context= {'user':user,'error':error_list}
        return render(request,template,context)

def scrape_update(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')
    elif not(role_ob.special_role2 == "master"): 
    	return redirect('master')

    else:
        template='smt_smpo_dashboard/scrape_update.html'
        #prompt = {'order' : 'Order of xlsx should be rda, website, product_type , brand , allocated_month , phase' }
        if str(request.POST.get('form-group'))=="template":
            query_chk=brand_program.objects.filter(first_level_ssp_status__isnull=True)
        	#print(query_chk[0].incremental_sku_coverage)
            if query_chk:
                col1='bid'
                col2='First level SSP status'
                col3='# keys avl in website'
                col4='IDF+AV_Overall performance'
                col5='IDF+AV+SSL_Overall performance'
                col6='Actionable for Backfill?'
                col7='# of keys'
                col8='Scrape SSP for SSL triggered'
                col9='ec_partition_id(website_id)'
                col10='Scrape metric > 20%'
                col11='# keys > 20'

                df_output = pd.DataFrame(columns=[col1,col2,col3,col4,col5,col6,col7,col8,col9,col10,col11]) 
                for row in range(len(query_chk)):

                    df_output.loc[row,'bid']=query_chk[row].bid
                    df_output.loc[row,'ec_partition_id(website_id)']=query_chk[row].website_id
        	#et=export_template(col1,col2,col3,col4,col5,col6,col7,col8,col9)
        	#print(et)
            else:
                df_output = pd.DataFrame(columns=['No Data matching the conditions'])
            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df_output.to_excel(xlwriter, 'sheetname',index=False)
            xlwriter.save()
            xlwriter.close()
            excel_file.seek(0)
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=template.xlsx'
            return response
        	#return et
        #else:
        if request.method == 'GET':
            return render(request, template)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        #print(a)
        error_list = []
        bb=0
        for x in a:
            chk=0
            for i in range(len(x)):

                if (pd.isnull(x[i])):
                    error_list.append('Row with BID '+str(x[0])+'has empty values')
                    chk+=1
            if(chk==0):
                db1= brand_program.objects.filter(bid=int(x[0]))
                if db1:
                    db1= brand_program.objects.get(bid=int(x[0]))
                    db1.first_level_ssp_status=str(x[1])
                    db1.keys_available_website_count=str(x[2])
                    db1.idf_av_performance=str(x[3])
                    db1.idf_av_ssl_performance=str(x[4])
                    db1.is_backfill=str(x[5])
                    db1.keys_count=str(x[6])
                    db1.scrape_ssp_status=str(x[7])
                    db1.website_id=str(x[8])
                    db1.scrape_metric=str(x[9])
                    db1.keys_count_gt_20=str(x[10])
                    bb+=1
                    try:
                        #print(db1)
                        db1.save()
                    except Exception as e:
                        error_list.append(e)
                        #print(e)
                else:
                    error_list.append(db1)
            
        context= {'user':user,'error':error_list}
        return render(request,template,context)

#DB2=brand_program.objects.create(brand=str(x[0]),website=str(x[1]),program_usecase=str(x[2]),mkpl=str(x[3]),mp_id=str(x[4]),language=str(x[5]),business_request=str(x[6]),brand_iteration=str(x[7]))
def backfill_request(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')
    elif not(role_ob.special_role2 == "master"): 
    	return redirect('master')

    else:
        template='smt_smpo_dashboard/backfill_request.html'
        #prompt = {'order' : 'Order of xlsx should be rda, website, product_type , brand , allocated_month , phase' }
        
        if str(request.POST.get('form-group'))=="template":
            query_chk=brand_program.objects.filter(uec_reflection_status__isnull=True)
            #print(query_chk[0].incremental_sku_coverage)
            if query_chk:

                col1='bid'
                col2='UEC reflecting'
                col3='SSL Is Auto-KVP completed'
                col4='ec_partition_id(website_id)'
                col5='backfill_type'

                df_output = pd.DataFrame(columns=[col1,col2,col3,col4,col5]) 
                for row in range(len(query_chk)):

                    df_output.loc[row,'bid']=query_chk[row].bid
                    df_output.loc[row,'ec_partition_id(website_id)']=query_chk[row].website_id
            #et=export_template(col1,col2,col3,col4,col5,col6,col7,col8,col9)
            #print(et)
            else:
                df_output = pd.DataFrame(columns=['No Data matching the conditions'])
            
            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df_output.to_excel(xlwriter, 'sheetname',index=False)
            xlwriter.save()
            xlwriter.close()
            excel_file.seek(0)
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=template.xlsx'
            return response
        if request.method == 'GET':
            return render(request, template)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        #print(a)
        error_list = []
        for x in a:
            chk=0
            for i in range(len(x)):

                if (pd.isnull(x[i])):
                    error_list.append('Row with BID '+str(x[0])+'has empty values')
                    chk+=1
            if(chk==0):
                db1= brand_program.objects.filter(bid=int(x[0]))
                if(db1):
                    db1= brand_program.objects.get(bid=int(x[0]))
                    db1.uec_reflection_status=str(x[1])
                    db1.ssl_auto_kvp_status=str(x[2])
                    db1.website_id=str(x[3])
                    try:
                        #print(db1)
                        db1.save()
                    except Exception as e:
                        error_list.append(e)
                else:
                    error_list.append(db1)
            
        context= {'user':user,'error':error_list}
        return render(request,template,context)
def matching_status(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')
    elif not(role_ob.special_role2 == "master"): 
    	return redirect('master')

    else:
        template='smt_smpo_dashboard/matching_status.html'
        #prompt = {'order' : 'Order of xlsx should be rda, website, product_type , brand , allocated_month , phase' }
        
        if str(request.POST.get('form-group'))=="template":
            query_chk=brand_program.objects.filter(matching_status__isnull=True)
            if query_chk:
                col1='bid'
                col2='Matching Status'
                col3='Matching start date'
                col4='Matching GV coverage'
                col5='Matching sku coverage'
                col6='Matching model'
                col7='ec_partition_id(website_id)'

                df_output = pd.DataFrame(columns=[col1,col2,col3,col4,col5,col6,col7]) 
                for row in range(len(query_chk)):

                    df_output.loc[row,'bid']=query_chk[row].bid
                    df_output.loc[row,'ec_partition_id(website_id)']=query_chk[row].website_id
            #et=export_template(col1,col2,col3,col4,col5,col6,col7,col8,col9)
            #print(et)
            else:
                df_output = pd.DataFrame(columns=['No Data matching the conditions'])
            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df_output.to_excel(xlwriter, 'sheetname',index=False)
            xlwriter.save()
            xlwriter.close()
            excel_file.seek(0)
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=template.xlsx'
            return response
        if request.method == 'GET':
            return render(request, template)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        #print(a)
        error_list = []
        for x in a:
            chk=0
            for i in range(len(x)):

                if (pd.isnull(x[i])):
                    error_list.append('Row with BID '+str(x[0])+'has empty values')
                    chk+=1
            if(chk==0):
                db1= brand_program.objects.filter(bid=int(x[0]))
                if db1:
                    db1= brand_program.objects.get(bid=int(x[0]))
                    db1.matching_status=str(x[1])
                    #str_matching_start_date = datetime.strptime(str(x[2]), "%Y-%m-%dT%H:%M:%S.%fZ")
                    db1.matching_start_date=x[2]
                    db1.matching_gv_coverage=str(x[3])
                    db1.matching_sku_coverage=str(x[4])
                    db1.matching_model=str(x[5])
                    db1.website_id=str(x[6])
                    try:
                        #print(db1)
                        db1.save()
                    except Exception as e:
                        error_list.append(e)
                else:
                    error_list.append(db1)
            
        context= {'user':user,'error':error_list}
        return render(request,template,context)
def incremental_status(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')
    elif not(role_ob.special_role2 == "master"): 
    	return redirect('master')

    else:
        template='smt_smpo_dashboard/incremental_status.html'
        #prompt = {'order' : 'Order of xlsx should be rda, website, product_type , brand , allocated_month , phase' }
        if str(request.POST.get('form-group'))=="template":
            query_chk=brand_program.objects.filter(is_incremental_matching__isnull=True)
            if query_chk:
                col1='bid'
                col2='Incremenal matching completed?'
                col3='Incremental matching GV coverage'
                col4='Incremental sku coverage'
                col5='ec_partition_id(website_id)'

                df_output = pd.DataFrame(columns=[col1,col2,col3,col4,col5]) 
                for row in range(len(query_chk)):

                    df_output.loc[row,'bid']=query_chk[row].bid
                    df_output.loc[row,'ec_partition_id(website_id)']=query_chk[row].website_id
            #et=export_template(col1,col2,col3,col4,col5,col6,col7,col8,col9)
            #print(et)
            else:
                df_output = pd.DataFrame(columns=['No Data matching the conditions'])
            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df_output.to_excel(xlwriter, 'sheetname',index=False)
            xlwriter.save()
            xlwriter.close()
            excel_file.seek(0)
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=template.xlsx'
            return response
        if request.method == 'GET':
            return render(request, template)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        #print(a)
        error_list = []
        for x in a:
            chk=0
            for i in range(len(x)):

                if (pd.isnull(x[i])):
                    error_list.append('Row with BID '+str(x[0])+'has empty values')
                    chk+=1
            if(chk==0):
                db1= brand_program.objects.filter(bid=int(x[0]))
                if db1:
                    db1= brand_program.objects.get(bid=int(x[0]))
                    db1.is_incremental_matching=str(x[1])
                    db1.incremental_matching_gv_coverage=str(x[2])
                    db1.incremental_sku_coverage=str(x[3])
                    db1.website_id=str(x[4])

                    try:
                        #print(db1)
                        db1.save()
                    except Exception as e:
                        error_list.append(e)
                else:
                    error_list.append(db1)
            
        context= {'user':user,'error':error_list}
        return render(request,template,context)
def update_identity_datapoints(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')
    elif not(role_ob.special_role2 == "master"): 
    	return redirect('master')

    else:
        template='smt_smpo_dashboard/update_identity_datapoints.html'
        #prompt = {'order' : 'Order of xlsx should be rda, website, product_type , brand , allocated_month , phase' }
        
        if str(request.POST.get('form-group'))=="template":
            query_chk=brand_program.objects.filter(identity_dp_backfill_status__isnull=True)
            if query_chk:
                col1='bid'
                col2='Identitiy DP scraped for backfill'
                col3='ec_partition_id(website_id)'

                df_output = pd.DataFrame(columns=[col1,col2,col3])
                for row in range(len(query_chk)):

                    df_output.loc[row,'bid']=query_chk[row].bid
                    df_output.loc[row,'ec_partition_id(website_id)']=query_chk[row].website_id
            #et=export_template(col1,col2,col3,col4,col5,col6,col7,col8,col9)
            #print(et)
            else:
                df_output = pd.DataFrame(columns=['No Data matching the conditions'])
            
            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df_output.to_excel(xlwriter, 'sheetname',index=False)
            xlwriter.save()
            xlwriter.close()
            excel_file.seek(0)
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=template.xlsx'
            return response
        if request.method == 'GET':
            return render(request, template)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        #print(a)
        error_list = []
        for x in a:
            chk=0
            for i in range(len(x)):

                if (pd.isnull(x[i])):
                    error_list.append('Row with BID '+str(x[0])+'has empty values')
                    chk+=1
            if(chk==0):
                db1= brand_program.objects.filter(bid=int(x[0]))
                if db1:
                    db1= brand_program.objects.get(bid=int(x[0]))
                    db1.identity_dp_backfill_status=str(x[1])
                    db1.website_id=str(x[2])

                    try:
                        #print(db1)
                        db1.save()
                    except Exception as e:
                        error_list.append(e)
                else:
                    error_list.append(db1)
            
        context= {'user':user,'error':error_list}
        return render(request,template,context)
def component_update(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')
    elif not(role_ob.special_role2 == "master"): 
    	return redirect('master')

    else:
        template='smt_smpo_dashboard/component_update.html'
        #prompt = {'order' : 'Order of xlsx should be rda, website, product_type , brand , allocated_month , phase' }
        
        if str(request.POST.get('form-group'))=="template":
            query_chk=brand_program.objects.filter(slots_backfilled_count__isnull=True)
            if query_chk:
                col1='bid'
                col2='# of slots backfilled'
                col3='ec_partition_id(website_id)'

                df_output = pd.DataFrame(columns=[col1,col2,col3]) 
                for row in range(len(query_chk)):

                    df_output.loc[row,'bid']=query_chk[row].bid
                    df_output.loc[row,'ec_partition_id(website_id)']=query_chk[row].website_id
            #et=export_template(col1,col2,col3,col4,col5,col6,col7,col8,col9)
            #print(et)
            else:
                df_output = pd.DataFrame(columns=['No Data matching the conditions'])
            
            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df_output.to_excel(xlwriter, 'sheetname',index=False)
            xlwriter.save()
            xlwriter.close()
            excel_file.seek(0)
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=template.xlsx'
            return response
        if request.method == 'GET':
            return render(request, template)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        #print(a)
        error_list = []
        for x in a:
            chk=0
            for i in range(len(x)):

                if (pd.isnull(x[i])):
                    error_list.append('Row with BID '+str(x[0])+'has empty values')
                    chk+=1
            if(chk==0):
                db1= brand_program.objects.filter(bid=int(x[0]))
                if db1:
                    db1= brand_program.objects.get(bid=int(x[0]))
                    db1.slots_backfilled_count=str(x[1])
                    db1.website_id=str(x[2])

                    try:
                        #print(db1)
                        db1.save()
                    except Exception as e:
                        error_list.append(e)
                else:
                    error_list.append(db1)
            
        context= {'user':user,'error':error_list}
        return render(request,template,context)
def tt_update(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')
    elif not(role_ob.special_role2 == "master"): 
    	return redirect('master')

    else:
        template='smt_smpo_dashboard/tt_update.html'
        #prompt = {'order' : 'Order of xlsx should be rda, website, product_type , brand , allocated_month , phase' }
        
        if str(request.POST.get('form-group'))=="template":
            query_chk=brand_program.objects.filter(tt_comments__isnull=True)
            if query_chk:
                col1='bid'
                col2='tt_comments'
                col3='ec_partition_id(website_id)'

                df_output = pd.DataFrame(columns=[col1,col2,col3]) 
                for row in range(len(query_chk)):

                    df_output.loc[row,'bid']=query_chk[row].bid
                    df_output.loc[row,'ec_partition_id(website_id)']=query_chk[row].website_id
            #et=export_template(col1,col2,col3,col4,col5,col6,col7,col8,col9)
            #print(et)
            else:
                df_output = pd.DataFrame(columns=['No Data matching the conditions'])
            
            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df_output.to_excel(xlwriter, 'sheetname',index=False)
            xlwriter.save()
            xlwriter.close()
            excel_file.seek(0)
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=template.xlsx'
            return response
        if request.method == 'GET':
            return render(request, template)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        #print(a)
        error_list = []
        for x in a:
            chk=0
            for i in range(len(x)):

                if (pd.isnull(x[i])):
                    error_list.append('Row with BID '+str(x[0])+'has empty values')
                    chk+=1
            if(chk==0):
                db1= brand_program.objects.filter(bid=int(x[0]))
                if db1:
                    db1= brand_program.objects.get(bid=int(x[0]))
                    db1.tt_comments=str(x[1])
                    db1.website_id=str(x[2])

                    try:
                        #print(db1)
                        db1.save()
                    except Exception as e:
                        error_list.append(e)
                else:
                    error_list.append(db1)
            
        context= {'user':user,'error':error_list}
        return render(request,template,context)
def update_business_usecase(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')
    elif not(role_ob.special_role2 == "master"): 
    	return redirect('master')

    else:
        template='smt_smpo_dashboard/update_business_usecase.html'
        #prompt = {'order' : 'Order of xlsx should be rda, website, product_type , brand , allocated_month , phase' }
        if str(request.POST.get('form-group'))=="template":
            query_chk=brand_program.objects.filter(business_usecase__isnull=True)
            if query_chk:
                col1='bid'
                col2='Business Use case'
                col3='Backfill - Business use case backfill update'
                col4='ec_partition_id(website_id)'

                df_output = pd.DataFrame(columns=[col1,col2,col3]) 
                for row in range(len(query_chk)):

                    df_output.loc[row,'bid']=query_chk[row].bid
                    df_output.loc[row,'ec_partition_id(website_id)']=query_chk[row].website_id
            #et=export_template(col1,col2,col3,col4,col5,col6,col7,col8,col9)
            #print(et)
            else:
                df_output = pd.DataFrame(columns=['No Data matching the conditions'])
            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df_output.to_excel(xlwriter, 'sheetname',index=False)
            xlwriter.save()
            xlwriter.close()
            excel_file.seek(0)
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=template.xlsx'
            return response
        if request.method == 'GET':
            return render(request, template)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        #print(a)
        error_list = []
        for x in a:
            chk=0
            for i in range(len(x)):

                if (pd.isnull(x[i])):
                    error_list.append('Row with BID '+str(x[0])+'has empty values')
                    chk+=1
            if(chk==0):
                db1= brand_program.objects.filter(bid=int(x[0]))
                if db1:
                    db1= brand_program.objects.get(bid=int(x[0]))
                    db1.business_usecase=str(x[1])
                    db1.backfill_business_usecase=str(x[2])
                    db1.website_id=str(x[3])
                    try:
                        #print(db1)
                        db1.save()
                    except Exception as e:
                        error_list.append(e)
                else:
                    error_list.append(db1)
            
        context= {'user':user,'error':error_list}
        return render(request,template,context)
def update_funnel_details(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')
    elif not(role_ob.special_role2 == "master"): 
    	return redirect('master')

    else:
        template='smt_smpo_dashboard/update_funnel_details.html'
        #prompt = {'order' : 'Order of xlsx should be rda, website, product_type , brand , allocated_month , phase' }
        if str(request.POST.get('form-group'))=="template":
        	col1='bid'
        	col2='ec_partition_id(website_id)'
        	
        	et=export_template(col1,col2,col3,col4,col5,col6,col7,col8,col9)
        	#print(et)
        	return et
        if request.method == 'GET':
            return render(request, template)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        #print(a)
        error_list = []
        for x in a:
            chk=0
            for i in range(len(x)):

                if (pd.isnull(x[i])):
                    error_list.append('col ')
                    chk+=1
            if(chk==0):
                db1= brand_program.objects.filter(bid=int(x[0]))
                if db1:
                    db1= brand_program.objects.get(bid=int(x[0]))
                    db1.website_id=str(x[1])

                    try:
                        #print(db1)
                        db1.save()
                    except Exception as e:
                        error_list.append(e)
                else:
                    error_list.append(db1)
            
        context= {'user':user,'error':error_list}
        return render(request,template,context)
def update_e2e_funnel_details(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')
    elif not(role_ob.special_role2 == "master"): 
    	return redirect('master')

    else:
        template='smt_smpo_dashboard/update_e2e_funnel_details.html'
        #prompt = {'order' : 'Order of xlsx should be rda, website, product_type , brand , allocated_month , phase' }
        if str(request.POST.get('form-group'))=="template":
        	col1='bid'
        	col2='ec_partition_id(website_id)'
        	
        	et=export_template(col1,col2,col3,col4,col5,col6,col7,col8,col9)
        	#print(et)
        	return et
        if request.method == 'GET':
            return render(request, template)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        #print(a)
        error_list = []
        for x in a:
            chk=0
            for i in range(len(x)):

                if (pd.isnull(x[i])):
                    error_list.append('Row with BID '+int(x[0])+'has empty values')
                    chk+=1
            if(chk==0):
                db1= brand_program.objects.filter(bid=int(x[0]))
                if db1:
                    db1= brand_program.objects.get(bid=int(x[0]))
                    db1.website_id=str(x[1])

                    try:
                        #print(db1)
                        db1.save()
                    except Exception as e:
                        error_list.append(e)
                else:
                    error_list.append(db1)
            
        context= {'user':user,'error':error_list}
        return render(request,template,context)

def export_template(col1,col2,col3,col4,col5,col6,col7,col8,col9):
	df_output = pd.DataFrame(columns=[col1,col2,col3,col4,col5,col6,col7,col8,col9]) 
	excel_file = IO()
	xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
	df_output.to_excel(xlwriter, 'sheetname',index=False)

	xlwriter.save()
	xlwriter.close()
	excel_file.seek(0)
	response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
	response['Content-Disposition'] = 'attachment; filename=template.xlsx'
	return response

def bs_alloc(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')

    else:
        template='smt_smpo_dashboard/bs_alloc.html'
        #prompt = {'order' : 'Order of xlsx should be rda, website, product_type , brand , allocated_month , phase' }
        data=[]
        if str(request.POST.get('form-group'))=="template":
        	db2= brand_ops.objects.filter(bs_status__isnull=True)
        	#print(db2)
        	
        	df_output = pd.DataFrame(list(db2.values())) 
        	df_output=df_output[['bid','brand','website']]
        	excel_file = IO()
        	xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        	df_output.to_excel(xlwriter, 'sheetname',index=False)

        	xlwriter.save()
        	xlwriter.close()
        	excel_file.seek(0)
        	response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        	response['Content-Disposition'] = 'attachment; filename=bs_alloc.xlsx'
        	return response
			
        if request.method == 'GET':
            return render(request, template)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        #print(a)
        error_list = []
        for x in a:
            db1= brand_ops.objects.get(bid=str(x[0]),bs_status__isnull=True)
            if db1:
            	#db1.website=str(x[1])
            	db1.bs_status='YTS'
            	db1.bs_owner=str(x[3])
            	db1.save()
            else:
                error_list.append(db1)
            
        context= {'user':user,'error':error_list}
        return render(request,template,context)

def bsv_alloc(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    obj = profile.objects.all().filter(user_role='auditor') | profile.objects.all().filter(user_role='sme')
    if not ob:
        return redirect('login')

    else:
        template='smt_smpo_dashboard/bsv_alloc.html'

        db1 = brand_ops.objects.all().filter(bs_status='Completed', bsv_status__isnull=True )
        #print(db1)
        data=[]

        if request.POST:
        	db2= brand_ops.objects.get(bid=str(request.POST.get('id')))
        	#print(str(request.POST.get('id')))
        	if db2:
        		db2.bsv_status='YTS'
        		db2.bsv_owner=str(request.POST.get('auditor'))

        		db2.save()
        context= {'user':user,'data':db1,'obj':obj}
        return render(request,template,context)
def ptv_alloc(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    obj = profile.objects.all().filter(user_role='auditor') | profile.objects.all().filter(user_role='sme')
    if not ob:
        return redirect('login')

    else:
        template='smt_smpo_dashboard/ptv_alloc.html'

        db1 = brand_ops.objects.all().filter(ptc_status='Completed', ptv_status__isnull=True )
        #print(db1)
        data=[]

        if request.POST:
        	db2= brand_ops.objects.get(bid=str(request.POST.get('id')))
        	#print(str(request.POST.get('id')))
        	if db2:
        		db2.ptv_status='YTS'
        		db2.ptv_owner=str(request.POST.get('auditor'))

        		db2.save()
        context= {'user':user,'data':db1,'obj':obj}
        return render(request,template,context)

def bem_alloc(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    obj = profile.objects.all().filter(user_role='auditor') | profile.objects.all().filter(user_role='sme')
    if not ob:
        return redirect('login')

    else:
        template='smt_smpo_dashboard/bem_alloc.html'

        db1 = brand_ops.objects.all().filter(backfill_status='Completed', bem_status__isnull=True )
        #print(db1)
        data=[]

        if request.POST:
        	db2= brand_ops.objects.get(bid=str(request.POST.get('id')))
        	#print(str(request.POST.get('id')))
        	if db2:
        		db2.bem_status='YTS'
        		db2.bem_owner=str(request.POST.get('auditor'))
        		db2.published_status='YTS'
        		db2.published_owner=user

        		db2.save()
        context= {'user':user,'data':db1,'obj':obj}
        return render(request,template,context)

def ptc_alloc(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')

    else:
        template='smt_smpo_dashboard/ptc_alloc.html'
        #prompt = {'order' : 'Order of xlsx should be rda, website, product_type , brand , allocated_month , phase' }
        #data=[]
        if str(request.POST.get('form-group'))=="template":
        	db2= brand_ops.objects.filter(ptc_status__isnull=True)
        	print(db2)

        	df_output = pd.DataFrame(list(db2.values())) 
        	df_output=df_output[['bid','brand','website']]
        	excel_file = IO()
        	xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        	df_output.to_excel(xlwriter, 'sheetname',index=False)

        	xlwriter.save()
        	xlwriter.close()
        	excel_file.seek(0)
        	response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        	response['Content-Disposition'] = 'attachment; filename=ptc_alloc.xlsx'
        	return response
			
        if request.method == 'GET':
            return render(request, template)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        print(a)
        error_list = []
        for x in a:
            db1= brand_ops.objects.get(bid=str(x[0]),ptc_status__isnull=True)
            if db1:
            	db1.ptc_status='YTS'
            	#db1.brand=str(x[2])
            	db1.ptc_owner=str(x[4])
            	db1.save()
            else:
                error_list.append(db1)
            
        context= {'user':user,'error':error_list}
        return render(request,template,context)
def backfill_alloc(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)

    if not ob:
        return redirect('login')

    else:
        template='smt_smpo_dashboard/backfill_alloc.html'
        #prompt = {'order' : 'Order of xlsx should be rda, website, product_type , brand , allocated_month , phase' }
        if str(request.POST.get('form-group'))=="template":
        	db2= brand_ops.objects.filter(backfill_status__isnull=True)
        	print(db2)
        	
        	df_output = pd.DataFrame(list(db2.values())) 
        	df_output=df_output[['bid','brand','website']]
        	excel_file = IO()
        	xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        	df_output.to_excel(xlwriter, 'sheetname',index=False)

        	xlwriter.save()
        	xlwriter.close()
        	excel_file.seek(0)
        	response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        	response['Content-Disposition'] = 'attachment; filename=backfill_alloc.xlsx'
        	return response
			
        if request.method == 'GET':
            return render(request, template)

        XLX_FILE = request.FILES['file_name']
        df = pd.read_excel(XLX_FILE)
        a = df.values.tolist()
        print(a)
        error_list = []
        for x in a:
            db1= brand_ops.objects.get(bid=str(x[0]),backfill_status__isnull=True)
            if db1:
            	db1.backfill_status='YTS'
            	#db1.brand=str(x[2])
            	db1.backfill_owner=str(x[4])
            	db1.save()
            else:
                error_list.append(db1)
            
        context= {'user':user,'error':error_list}
        return render(request,template,context)

def bs_realloc(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    obj = profile.objects.all().filter(user_role='auditor') | profile.objects.all().filter(user_role='sme')
    db1=[]
    if not ob:
        return redirect('login')

    else:
        template='smt_smpo_dashboard/bs_realloc.html'

        if request.POST:
        	#print('hi')
        	if str(request.POST.get('form-group'))=="brand_search":
        		#print('hi')
        		db1 = brand_ops.objects.all().filter(brand__contains= str(request.POST.get('brand_search')))

        		context= {'user':user,'data':db1,'obj':obj}
        		return render(request,template,context)
        	else:
        		db2= brand_ops.objects.get(bid=str(request.POST.get('id')))
        	#print(str(request.POST.get('id')))
        		if db2:
        			db2.bs_owner=str(request.POST.get('auditor'))

        			db2.save()

    context= {'user':user,'data':db1,'obj':obj}
    return render(request,template,context)
def bsv_realloc(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    obj = profile.objects.all().filter(user_role='auditor') | profile.objects.all().filter(user_role='sme')
    db1=[]
    if not ob:
        return redirect('login')

    else:
        template='smt_smpo_dashboard/bsv_realloc.html'

        if request.POST:
        	if str(request.POST.get('form-group'))=="brand_search":
        		db1 = brand_ops.objects.all().filter(brand= str(request.POST.get('brand_search')))
        #print(db1)
        	else:
        		db2= brand_ops.objects.get(bid=str(request.POST.get('id')))
        	#print(str(request.POST.get('id')))
        		if db2:

        			db2.bsv_owner=str(request.POST.get('auditor'))

        			db2.save()
        context= {'user':user,'data':db1,'obj':obj}
        return render(request,template,context)

def ptc_realloc(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    obj = profile.objects.all().filter(user_role='auditor') | profile.objects.all().filter(user_role='sme')
    db1=[]
    if not ob:
        return redirect('login')

    else:
        template='smt_smpo_dashboard/ptc_realloc.html'

        if request.POST:
        	if str(request.POST.get('form-group'))=="brand_search":
        		db1 = brand_ops.objects.all().filter(brand= str(request.POST.get('brand_search')))
        #print(db1)

        	else:
        		db2= brand_ops.objects.get(bid=str(request.POST.get('id')))
        	#print(str(request.POST.get('id')))
        		if db2:

        			db2.ptc_owner=str(request.POST.get('auditor'))

        			db2.save()
        context= {'user':user,'data':db1,'obj':obj}
        return render(request,template,context)
def ptv_realloc(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    obj = profile.objects.all().filter(user_role='auditor') | profile.objects.all().filter(user_role='sme')
    db1=[]
    if not ob:
        return redirect('login')

    else:
        template='smt_smpo_dashboard/ptv_realloc.html'

        if request.POST:
        	if str(request.POST.get('form-group'))=="brand_search":
        		db1 = brand_ops.objects.all().filter(brand= str(request.POST.get('brand_search')))
        
        	else:
        		db2= brand_ops.objects.get(bid=str(request.POST.get('id')))
        	#print(str(request.POST.get('id')))
        		if db2:
        			db2.ptc_owner=str(request.POST.get('auditor'))

        			db2.save()
        context= {'user':user,'data':db1,'obj':obj}
        return render(request,template,context)
def backfill_realloc(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    obj = profile.objects.all().filter(user_role='auditor') | profile.objects.all().filter(user_role='sme')
    db1=[]
    if not ob:
        return redirect('login')

    else:
        template='smt_smpo_dashboard/backfill_realloc.html'

        if request.POST:
        	if str(request.POST.get('form-group'))=="brand_search":
        		db1 = brand_ops.objects.all().filter(brand= str(request.POST.get('brand_search')))

        	else:
        		db2= brand_ops.objects.get(bid=str(request.POST.get('id')))
        	#print(str(request.POST.get('id')))
        		if db2:

        			db2.backfill_owner=str(request.POST.get('auditor'))

        			db2.save()
        context= {'user':user,'data':db1,'obj':obj}
        return render(request,template,context)
def bem_realloc(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    obj = profile.objects.all().filter(user_role='auditor') | profile.objects.all().filter(user_role='sme')
    db1=[]
    if not ob:
        return redirect('login')

    else:
        template='smt_smpo_dashboard/bem_realloc.html'

        if request.POST:
        	if str(request.POST.get('form-group'))=="brand_search":
        		db1 = brand_ops.objects.all().filter(brand= str(request.POST.get('brand_search')))
        		#print(db1)

        	else:
        		db2= brand_ops.objects.get(bid=str(request.POST.get('id')))
        	#print(str(request.POST.get('id')))
        		if db2:

        			db2.bem_owner=str(request.POST.get('auditor'))

        			db2.save()
        context= {'user':user,'data':db1,'obj':obj}
        return render(request,template,context)
def publish_realloc(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    role_ob = profile.objects.get(user_name=user)
    obj = profile.objects.all().filter(user_role='auditor') | profile.objects.all().filter(user_role='sme')
    db1=[]
    if not ob:
        return redirect('login')

    else:
        template='smt_smpo_dashboard/publish_realloc.html'

        if request.POST:
        	if str(request.POST.get('form-group'))=="brand_search":
        		db1 = brand_ops.objects.all().filter(brand= str(request.POST.get('brand_search')))
        		#print(db1)

        	else:
        		db2= brand_ops.objects.get(bid=str(request.POST.get('id')))
        	#print(str(request.POST.get('id')))
        		if db2:
        			db2.published_owner=str(request.POST.get('auditor'))

        			db2.save()
        context= {'user':user,'data':db1,'obj':obj}
        return render(request,template,context)

def bnchmrk(request):
    current_user = request.user
    user= current_user.username

    obj = benchmark.objects.all()
    
    if request.POST:
        prod = benchmark.objects.create(task=str(request.POST.get('task')),subtask=str(request.POST.get('sub-task')),productivity=str(request.POST.get('product')))
        if str(request.POST.get('lower')) is not '':
            prod.lower_select = str(request.POST.get('lower'))
            prod.higher_select = str(request.POST.get('upper'))
            prod.lower_pt = str(request.POST.get('ptlower'))
            prod.higher_pt = str(request.POST.get('ptupper'))
            prod.complexity = str(request.POST.get('complex'))
            prod.parameter = str(request.POST.get('paramet'))
        prod.save()

    context = {'role':get_role(user),'user':user,'obj': obj,'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
    return render(request,'smt_smpo_dashboard/benchmark_metrics.html',context)

def quality(request):
    current_user = request.user
    user= current_user.username

    if request.method == 'GET':
        return render(request, 'smt_smpo_dashboard/quality.html', {'user':user,'order':'Order of xlsx file- associate, phase,quality score out of 100'})

    
    XLX_FILE = request.FILES['file_name']
    df = pd.read_excel(XLX_FILE)
    a = df.values.tolist()
    for x in a:
        ob = productivity.objects.create(user=str(x[0]),phase=str(x[1]),task=str(x[2]),brand="Quality")
        ob.timestamp = datetime.now()
        ob.save()
    return render(request,'smt_smpo_dashboard/quality.html',{'user':user,'order':'Order of xlsx file- associate, phase,quality score out of 100'})

def error_log(request):
    current_user = request.user
    user = current_user.username
  
    aoa = brand_ops.objects.all().filter(backfill_owner=user,bem_status='Completed')

    context={'user':user,'aoa':aoa,'role':get_role(user)}
    return render(request,'smt_smpo_dashboard/error_log.html',context)

def backfill_ops_summary(request):
    current_user = request.user
    user = current_user.username
    qry_chk=['Backfill issue','Backfill WIP - All Scrapes done','Backfill YTS - All Scrapes done','Backfilled','Backfilled with Zero slots - All Scrapes done','Brand Hold - Issues In PT-Classification','Identity not reflecting in Product attribute','Identity Scrape WIP','Incremental Matching WIP','Matching WIP','NameSpace Mapping dropped - All Scrapes done','Not Feasible with Auto-KVP','Not successful on Scrape - All Scrapes done','Publishing WIP','Scrape WIP - SSL Pending']
    prod_val=[]
    prod_val2=[]
    for q in qry_chk:
        ob1 = brand_program.objects.filter(overall_website_status=q,en_nonen='EN').count()
        #s1 = ob1.get('website_id__sum')
        if ob1 is None:
            prod_val.append({'h':q,'v':0})
        else:
            prod_val.append({'h':q,'v':int(ob1)})

        ob2 = brand_program.objects.filter(overall_website_status=q,en_nonen='Non-EN').count()
        #s1 = ob1.get('website_id__sum')
        if ob2 is None:
            prod_val2.append({'h':q,'v':0})
        else:
            prod_val2.append({'h':q,'v':int(ob2)})
    '''ob1 = brand_program.objects.filter(overall_website_status='Backfill WIP - All Scrapes done').aggregate(Sum('website_id'))
    s1 = ob1.get('website_id__sum')
    if s1 is None:
        prod_val.append(0)
    else:
        prod_val.append(int(s1))'''

    #template='smt_smpo_dashboard/ops_summary.html'
    return render(request,'smt_smpo_dashboard/backfill_ops_summary.html',{'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user),'user':user,'tot':prod_val,'tot2':prod_val2,'heads':qry_chk})

def rampup_table(request):
    current_user = request.user
    user = current_user.username

    delta = timedelta(days=1)

    start_date=datetime.today()
    start_date = start_date.replace(day=1)
    start_date2=start_date
    end_date=datetime.today().month
    #print(start_date.month+1)
        #print(start_date.strftime("%Y-%m"))
    #print(start_date.strftime("%Y-%m-%d"))
    m=1
    prod_val=['Current Status - Monthly']
    prod_val2=['Current Status - Cumulative']
    prod_val3=['Current Status - Monthly']
    prod_val4=['Current Status - Cumulative']
    tot1=0
    tot2=0
    ob3=brand_ops.objects.filter(backfill_status='completed',backfill_completion_date__year=start_date.year).count()
    #ob4=brand_ops.objects.filter(overall_website_status='completed',published_completion_date__year=start_date.year).count()
    ob4=brand_program.objects.filter(overall_website_status='completed')
    print(ob4.exists())
    if  ob4:
        obb4=brand_ops.objects.filter(ec_partition_id__in=ob4.website_id,published_completion_date__year=start_date.year).count()
    else:
        obb4=''
    '''ob1 = brand_ops.objects.filter(backfill_status='completed',backfill_completion_date__month=1).count()
    if ob1 is None:
        prod_val.append(0)
    else:
        prod_val.append(int(ob1))
    m2=1

    #ob2 = brand_program.objects.filter(overall_website_status='completed',published_completion_date__month=1).count()
    ob2=brand_program.objects.filter(overall_website_status='completed')
    ob22=brand_ops.filter(ec_partition_id__in=ob2.website_id,published_completion_date__gte=).count()
    if ob22 is None:
        prod_val2.append(0)
    else:
        prod_val2.append(int(ob22))'''

    while m <= end_date:
    #while start_date.month <= end_date:
        #date_range.append(start_date.strftime("%Y-%m"))
        print(m)
        if(m <=12):   
            start_date=start_date.replace(month=m)
            if(m==12):
                start_date2=start_date2.replace(month=m)
            else:
                start_date2=start_date2.replace(month=m+1)
            #print(start_date)
            d1=start_date.strftime('%Y-%m-%d')
            d2=start_date2.strftime('%Y-%m-%d')
            ob1 = brand_ops.objects.filter(backfill_status='completed',backfill_completion_date__gte=d1,backfill_completion_date__lte=d2).count()
            if ob1 is None:
                prod_val.append(0)
                tot1+=0
                prod_val3.append(tot1)
            else:
                prod_val.append(int(ob1))
                tot1+=int(ob1)
                prod_val3.append(tot1)
            
            ob2=brand_program.objects.filter(overall_website_status='completed')
            if ob2:
                ob22=brand_ops.filter(ec_partition_id__in=ob2.website_id,published_completion_date__gte=d1,published_completion_date__lte=d2).count()
                if ob22 is None:
                    prod_val2.append(0)
                    tot2+=0
                    prod_val4.append(tot2)
                else:
                    prod_val2.append(int(ob22))
                    tot2+=int(ob2)
                    prod_val4.append(tot2)
            else:
                prod_val2.append(0)
                tot2+=0
                prod_val4.append(tot2)
            m+=1
    return render(request,'smt_smpo_dashboard/rampup_table.html',{'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user),'user':user,'tot':prod_val,'tot2':prod_val2,'tot3':prod_val3,'tot4':prod_val4})

def eod_update(request):
    current_user = request.user
    user = current_user.username

    delta = timedelta(days=1)

    if request.POST:
        ph=request.POST.get('phase')
        s='01-'+str(ph)
        #print(s)
        start_date= datetime.strptime(s,'%d-%m-%Y')
        #start_date=start_date.strptime(s,'%d-%m-%Y')
        #print(start_date)
        ed=ph.split('-')
        #print(ed)
        last_date=calendar.monthrange(int(ed[1]), int(ed[0]))[1]
        #print(last_date)
        s2=str(last_date)+'-'+str(ph)
        end_date= datetime.strptime(s2,'%d-%m-%Y')
        print(end_date)
        #end_date=request.POST.get('endDate')
        #end_date= datetime.strptime(end_date,'%Y-%m-%d')
    else:
        start_date=datetime.today()
        start_date = start_date.replace(day=1)
        end_date=datetime.today()
    #print(start_date)
    #print(end_date)
    #print(start_date.month+1)
        #print(start_date.strftime("%Y-%m"))
    m=0
    prod_val=['NM Executed']
    prod_val2=['Backfilled']
    prod_val3=['Backfilled with Zero slots - All Scrapes done']
    prod_val4=['NameSpace Mapping dropped - All Scrapes done']
    prod_val5=['NM Executed']
    prod_val6=['Backfilled']
    prod_val7=['Backfilled with Zero slots - All Scrapes done']
    prod_val8=['NameSpace Mapping dropped - All Scrapes done']
    prod_val9=['NM Executed']
    prod_val10=['Backfilled']
    prod_val11=['Backfilled with Zero slots - All Scrapes done']
    prod_val12=['NameSpace Mapping dropped - All Scrapes done']
    print_date_range=[]

    while start_date < end_date:
    #while start_date.month <= end_date:
        #date_range.append(start_date.strftime("%Y-%m"))
        print(start_date)
        print(type(start_date))
        m+=1
        start_date=start_date.replace(day=m)
        holiday = start_date.weekday()
        d1=start_date
        #print(m)
        #print(holiday)
            #print(start_date)
        if(holiday<6):
            print_date_range.append(start_date.strftime("%d-%b"))
            ob1 = brand_ops.objects.filter(backfill_status='completed',backfill_completion_date=d1.strftime("%Y-%m-%d")).count()
            if ob1 is None:
                prod_val.append(0)
            else:
                prod_val.append(int(ob1))
            
            ob2=brand_program.objects.filter(overall_website_status='backfilled')
            if ob2:
                ob22=brand_ops.filter(ec_partition_id__in=ob2.website_id,published_completion_date=d1.strftime("%Y-%m-%d")).count()
                if ob22 is None:
                    prod_val2.append(0)
                else:
                    prod_val2.append(int(ob22))
            else:
                prod_val2.append(0)
            ob3=brand_program.objects.filter(overall_website_status='Backfilled with Zero slots - All Scrapes done')
            if ob3:
                ob32=brand_ops.filter(ec_partition_id__in=ob3.website_id,published_completion_date=d1.strftime("%Y-%m-%d")).count()
                if ob32 is None:
                    prod_val3.append(0)
                else:
                    prod_val3.append(int(ob32))
            else:
                prod_val3.append(0)
            ob4 = brand_ops.objects.filter(backfill_status='completed',backfill_completion_date=d1.strftime("%Y-%m-%d")).count()
            if ob4 is None:
                prod_val4.append(0)
            else:
                prod_val4.append(int(ob4))
######
            ob5 = brand_ops.objects.filter(backfill_status='completed',language='English',backfill_completion_date=d1.strftime("%Y-%m-%d")).count()
            if ob5 is None:
                prod_val5.append(0)
            else:
                prod_val5.append(int(ob5))
            
            ob6=brand_program.objects.filter(overall_website_status='backfilled')
            if ob6:
                ob62=brand_ops.filter(ec_partition_id__in=ob6.website_id,language='English',published_completion_date=d1.strftime("%Y-%m-%d")).count()
                if ob62 is None:
                    prod_val6.append(0)
                else:
                    prod_val6.append(int(ob62))
            else:
                prod_val6.append(0)
            ob7=brand_program.objects.filter(overall_website_status='Backfilled with Zero slots - All Scrapes done')
            if ob7:
                ob72=brand_ops.filter(ec_partition_id__in=ob7.website_id,language='English',published_completion_date=d1.strftime("%Y-%m-%d")).count()
                if ob72 is None:
                    prod_val7.append(0)
                else:
                    prod_val7.append(int(ob72))
            else:
                prod_val7.append(0)
            ob8 = brand_ops.objects.filter(backfill_status='completed',language='English',backfill_completion_date=d1.strftime("%Y-%m-%d")).count()
            if ob8 is None:
                prod_val8.append(0)
            else:
                prod_val8.append(int(ob8))

######      
            ob9 = brand_ops.objects.filter(backfill_status='completed',language='Other',backfill_completion_date=d1.strftime("%Y-%m-%d")).count()
            if ob9 is None:
                prod_val9.append(0)
            else:
                prod_val9.append(int(ob9))
            
            ob10=brand_program.objects.filter(overall_website_status='backfilled')
            if ob10:
                ob102=brand_ops.filter(ec_partition_id__in=ob10.website_id,language='Other',published_completion_date=d1.strftime("%Y-%m-%d")).count()
                if ob22 is None:
                    prod_val10.append(0)
                else:
                    prod_val10.append(int(ob102))
            else:
                prod_val10.append(0)
            ob11=brand_program.objects.filter(overall_website_status='Backfilled with Zero slots - All Scrapes done')
            if ob11:
                ob112=brand_ops.filter(ec_partition_id__in=ob11.website_id,language='Other',published_completion_date=d1.strftime("%Y-%m-%d")).count()
                if ob112 is None:
                    prod_val11.append(0)
                else:
                    prod_val11.append(int(ob112))
            else:
                prod_val11.append(0)
            ob12 = brand_ops.objects.filter(backfill_status='completed',language='Other',backfill_completion_date=d1.strftime("%Y-%m-%d")).count()
            if ob12 is None:
                prod_val12.append(0)
            else:
                prod_val12.append(int(ob12))
    
    print(create_phase2())    
    p=create_phase2()
    p1=p[0]
    p2=p[1]


    return render(request,'smt_smpo_dashboard/eod_update.html',{'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user),'user':user,'PHASE':create_phase2(),'print_date_range':print_date_range,'tot1':prod_val,'tot2':prod_val2,'tot3':prod_val3,'tot4':prod_val4,'tot5':prod_val5,'tot6':prod_val6,'tot7':prod_val7,'tot8':prod_val8,'tot9':prod_val9,'tot10':prod_val10,'tot11':prod_val11,'tot12':prod_val12})
    
def refresh_button(request):
    current_user = request.user
    user = current_user.username
    today = datetime.today()
    role_ob = profile.objects.get(user_name=user)
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    #print('hi')
    mp_id_chk=['4','5','35691', '44551', '6']
    if not ob:
        return redirect('login')
    #elif not(role_ob.special_role2 == "master"): 
        #return redirect('master')

    else:
        template='smt_smpo_dashboard/master_homepage.html'

        if request.POST:
            #print('hi')
            a = brand_program.objects.all()
            for prog in a:
                prog_brand=str(prog.brand)
                prog_website=str(prog.website)
                prog_website_id=str(prog.website_id)
                prog_language=str(prog.language)
                prog_bus_request=str(prog.business_request)
                prog_iter=str(prog.brand_iteration)
                prog_mkpl=str(prog.mkpl)
                prog_priority=str(prog.priority)
                h= str(prog.scrape_metric)
                k=str(prog.keys_count_gt_20)
                s=str(prog.ec_gv_matching_cvg_gt_20)
                prog_ssl_auto_kvp_status=str(prog.ssl_auto_kvp_status)
                prog_matching_status=str(prog.matching_status)
                prog_matching_gv_coverage=str(prog.matching_gv_coverage)
                prog_backfill_source_attributes_count=prog.backfill_source_attributes_count
                prog_incremental_sku_coverage=prog.incremental_sku_coverage
                prog_matching_sku_coverage=prog.matching_sku_coverage
                #prog_matching_status=prog.matching_status
                prog_incremental_matching_gv_coverage=prog.incremental_matching_gv_coverage
                prog_scrape_status=prog.scrape_status
                prog_first_level_ssp_status=prog.first_level_ssp_status
                prog_ptc_status=prog.ptc_status
                prog_backfill_status=prog.backfill_status
                prog_backfill_type=prog.backfill_type
                prog_overall_website_status=prog.overall_website_status
                prog_mp_id=prog.mp_id
                #print(h)
                #print(k)
                #print(s)
                
                ops= brand_ops.objects.create(brand=prog_brand,website=prog_website,ec_partition_id=prog_website_id,language=prog_language,business_request=prog_bus_request,validation_sample_selection=prog_backfill_source_attributes_count,mkpl=prog_mkpl,backfill_type=prog_backfill_type,brand_iteration=prog_iter)
                
                
                #if(ops_select.published_status=='completed'):

                ops.save()       
                ops_select=brand_ops.objects.all.filter(ec_partition_id=prog_website_id)              
                published_status=ops_select.published_status
                backfill_status=ops_select.backfill_status
                slots_backfilled_count=ops_select.slots_backfilled_count
                bem_converted=ops_select.bem_converted
                ops_ptc=ops_select.ptc_status
                ops_bem_status=ops_select.bem_status
                ops_backfill_status=ops_select.backfill_status
                ops_vv_nam_dropped=ops_select.vv_nam_dropped

                ops_bs_comments=str(ops_select.bs_comments)
                ops_bsv_comments=str(ops_select.bsv_comments)
                ops_ptc_comments=str(ops_select.ptc_comments)
                ops_ptv_comments=str(ops_select.ptv_comments)
                ops_backfill_comments=str(ops_select.backfill_comments)
                ops_bem_publish_comment=str(ops_select.bem_publish_comment)
                detailed_backfill_status_val='BS-'+ops_bs_comments+' |BSV-'+ops_bsv_comments+' |PTC-'+ops_ptc_comments+' |PTV-'+ops_ptv_comments+' |NMVV-'+ops_backfill_comments+' |BEM'+ops_bem_publish_comment

                prog.ptc_status=ops_ptc
                prog.backfill_status=ops_backfill_status
                prog.bem_status=ops_bem_status
                prog.priority='s'
                if(h=="Y" and s=="Y" and k=="Y"):
                    #print('hi')
                    prog.priority="P1"
                elif(h=="N" and s=="Y" and k=="Y"):
                    prog.priority="P2"
                elif(h=="N" and s=="Y" and k=="N"):
                    prog.priority="P3"
                elif(h=="Y" and s=="N" and k=="Y"):
                    prog.priority="P3"
                elif(h=="Y" and s=="Y" and k=="N"):
                    prog.priority="P3"
                elif(h=="N" and s=="N" and k=="Y"):
                    prog.priority="P3"
                elif(h=="N" and s=="N" and k=="N"):
                    prog.priority="P4"
                elif(h=="Y" and s=="N" and k=="N"):
                    prog.priority="P4"
                else:
                    prog.priority="YTD"
                if h=='Zero scrape':
                    prog.overall_website_status='Not successful on Scrape - All Scrapes done'
                #c1=prog_incremental_sku_coverage
                if(prog_incremental_sku_coverage=='' and prog_matching_sku_coverage==''):
                    if not(prog_matching_status==''):
                        prog.ec_gv_matching_cvg_gt_20=='YTC'
                elif(prog_incremental_sku_coverage>20 or prog_incremental_matching_gv_coverage>20):
                    prog.ec_gv_matching_cvg_gt_20=='Y'
                elif(prog_matching_gv_coverage>20 or prog_matching_sku_coverage>20):
                    prog.ec_gv_matching_cvg_gt_20=='Y'
                else:
                    prog.ec_gv_matching_cvg_gt_20=='N'

                if(published_status=='Completed'):
                    prog.overall_website_status='Backfilled'
                    prog.month=datetime.today()
                    if(slots_backfilled_count==0):
                        prog.overall_website_status='Backfilled with Zero slots - All Scrapes done'
                elif(backfill_status=='VV Completed'):
                    prog.overall_website_status='Backfill WIP - All Scrapes done'
                    prog.nm_status='NM WIP'
                    if(vv_nam_dropped=='yes'):
                        prog.overall_website_status='NameSpace Mapping dropped - All Scrapes done'
                if('ublished' in backfill_status):
                    prog.nm_status='NM WIP'
                if('ompleted' in ptc_status):
                    prog.ptc_status='y'
                if(flag_overall_website_status=='' or not(flag_overall_website_status=='f1')):
                    if(prog_ssl_auto_kvp_status=='Yes' or 'ompleted' in prog_scrape_status ):
                        if(prog_matching_status=='Yes' and s=='N' and (prog_matching_gv_coverage=='')):
                            prog.overall_website_status='Incremental Matching WIP'

                        if(prog_matching_status==''):
                            prog.overall_website_status='Matching WIP'
                        if(s=='Y' and k=='Y'):
                            prog.overall_website_status='Backfill YTS - All Scrapes done'

                    elif(not(prog_ssl_auto_kvp_status=='Yes') or 'ompleted' not in prog_scrape_status ):
                        prog.overall_website_status='Scrape WIP - SSL Pending'
                    if not(first_level_ssp_status=='SSP completed'):
                        prog.overall_website_status='Identity Scrape WIP'
                else:
                    if(prog_ptc_status=='on hold'):
                        prog.overall_website_status='Brand Hold - Issues In PT-Classification'
                    if(prog_backfill_status=='wip'):
                        prog.overall_website_status='Backfill WIP - All Scrapes done'
                    if(ops_backfill_status=='VV completed'  ):
                        if(published_status=='' or published_status=='YTS' or published_status=='WIP'):
                            prog.overall_website_status='Publishing wip'
                        if ops_vv_nam_dropped=='yes':
                            prog.overall_website_status='NameSpace Mapping dropped - All Scrapes done'
                    if(published_status=='completed'):
                        if(slots_backfilled_count==0):
                            prog.overall_website_status='Backfilled'
                        if(slots_backfilled_count>0):
                            prog.overall_website_status='Backfilled with Zero slots - All Scrapes done'
                if(prog_overall_website_status=='Backfilled with Zero slots - All Scrapes done' or prog_overall_website_status=='NameSpace Mapping dropped - All Scrapes done'):
                    prog.ds_queue='Yes'
                if (prog_mp_id in mp_id_chk):
                    prog.en_nonen='En'
                else:
                    prog.en_nonen='Non-En'
                #if not((bem_converted==0) or (bem_converted=='')):
                    #prog.is_bem_attempted='Yes'    
                prog.save()
        context= {'user':user}
        return render(request,template,context)

def bs_stat(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    if not ob:
        return redirect('login')
    else:
        xstat = ["YTS","WIP"]
        qs = brand_ops.objects.all().filter(bs_status__in=xstat)
        if request.POST:
            ob = brand_ops.objects.get(bid=str(request.POST.get('id')))
            ob.bs_status = str(request.POST.get('Subtask'))
            ob.save()

            pprod_mins = 0
            ben_ob = benchmark.objects.filter(task="Brand study",subtask="Completed")
            for i in ben_ob:
                p = int(i.productivity)
            pprod_mins = p*ob.bs_attributes_count    
                    
            if ob.bs_status == "Completed" : tot_prod = pprod_mins
            else : tot_prod = 0

            exists_obj = productivity.objects.all().filter(website=ob.website,brand=ob.brand,user=user,task=str(request.POST.get('task')),sub_task=str(request.POST.get('Subtask')),phase__icontains=datetime.today().year).count()
            if exists_obj==0:
                prod_stats = productivity.objects.create(website=ob.website,brand=ob.brand,user=user,task=str(request.POST.get('task')),sub_task=str(request.POST.get('Subtask')),phase=current_phase(),timestamp =datetime.now(),productivity = tot_prod)
                prod_stats.save()
                return redirect('bs_stat')
            else:
                prod_stats = productivity.objects.create(website=ob.website,brand=ob.brand,user=user,task=str(request.POST.get('task')),sub_task=str(request.POST.get('Subtask')),phase=current_phase(),timestamp =datetime.now(),productivity = int(0))
                prod_stats.save()
                return redirect('bs_stat')
        return render(request,'smt_smpo_dashboard/bs_stat_update.html',{'qs':qs,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)})

def bsv_stat(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    if not ob:
        return redirect('login')
    else:
        xstat = ["YTS","WIP"]
        qs = brand_ops.objects.all().filter(bs_status__in=xstat)
        if request.POST:
            ob = brand_ops.objects.get(bid=str(request.POST.get('id')))
            ob.bs_status = str(request.POST.get('Subtask'))
            ob.save()

            pprod_mins,p = 0,0
            ben_ob = benchmark.objects.filter(task="Brand study validation",subtask="Completed")
            for i in ben_ob:
                p = int(i.productivity)
            pprod_mins = p*ob.bsv_attributes_count    
                    
            if ob.bs_status == "Completed" : tot_prod = pprod_mins
            else : tot_prod = 0

            exists_obj = productivity.objects.all().filter(website=ob.website,brand=ob.brand,user=user,task=str(request.POST.get('task')),sub_task=str(request.POST.get('Subtask')),phase__icontains=datetime.today().year).count()
            if exists_obj==0:
                prod_stats = productivity.objects.create(website=ob.website,brand=ob.brand,user=user,task=str(request.POST.get('task')),sub_task=str(request.POST.get('Subtask')),phase=current_phase(),timestamp =datetime.now(),productivity = tot_prod)
                prod_stats.save()
                return redirect('bsv_stat')
            else:
                prod_stats = productivity.objects.create(website=ob.website,brand=ob.brand,user=user,task=str(request.POST.get('task')),sub_task=str(request.POST.get('Subtask')),phase=current_phase(),timestamp =datetime.now(),productivity = int(0))
                prod_stats.save()
                return redirect('bsv_stat')
        return render(request,'smt_smpo_dashboard/bsv_stat_update.html',{'qs':qs,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)})

def ptc_stat(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    obb =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    if not obb:
        return redirect('login')
    else:
        xstat = ["YTS","WIP"]
        qs = brand_ops.objects.all().filter(bs_status__in=xstat)
        if request.POST:
            ob = brand_ops.objects.get(bid=str(request.POST.get('id')))
            ob.bs_status = str(request.POST.get('Subtask'))
            ob.save()

            no_pt = ob.ptc_no_pt
            dist_tit = ob.ptc_distinct_title
            pprod_mins,comple,lang_val = 0,0,0
            if ob.language == "Others" : lang_val = 30
            else : lang_val = 0
            ben_ob = benchmark.objects.filter(task="PTC",subtask="Completed")
            for i in ben_ob:
                l = int(i.lower_pt)
                h = int(i.higher_pt)
                ll = int(i.lower_select)
                hh = int(i.higher_select)
                if no_pt>=l and no_pt<=h:
                    pprod_mins = i.productivity
                if dist_tit>=ll and dist_tit<=hh:
                    comple = i.complexity
            if ob.bs_status == "Completed" : tot_prod = (pprod_mins*comple)+lang_val
            else : tot_prod = 0
            prod_stats = productivity.objects.create(website=ob.website,brand=ob.brand,user=user,task=str(request.POST.get('task')),sub_task=str(request.POST.get('Subtask')),phase=current_phase(),timestamp =datetime.now(),productivity=tot_prod)
            prod_stats.save()
            return redirect('ptc_stat')
        return render(request,'smt_smpo_dashboard/ptc_stat_update.html',{'qs':qs,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)})

def ptv_stat(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    if not ob:
        return redirect('login')
    else:
        xstat = ["YTS","WIP"]
        qs = brand_ops.objects.all().filter(bs_status__in=xstat)
        if request.POST:
            ob = brand_ops.objects.get(bid=str(request.POST.get('id')))
            ob.bs_status = str(request.POST.get('Subtask'))
            ob.save()

            no_pt = ob.ptv_no_pt
            dist_tit = ob.ptv_distinct_title
            pprod_mins,comple,lang_val = 0,0,0
            if ob.language == "Others" : lang_val = 30
            else : lang_val = 0
            ben_ob = benchmark.objects.filter(task="PTV",subtask="Completed")
            for i in ben_ob:
                l = int(i.lower_pt)
                h = int(i.higher_pt)
                ll = int(i.lower_select)
                hh = int(i.higher_select)
                if no_pt>=l and no_pt<=h:
                    pprod_mins = i.productivity
                if dist_tit>=ll and dist_tit<=hh:
                    comple = i.complexity
            if ob.bs_status == "Completed" : tot_prod = (pprod_mins*comple)+lang_val
            else : tot_prod = 0
            prod_stats = productivity.objects.create(website=ob.website,brand=ob.brand,user=user,task=str(request.POST.get('task')),sub_task=str(request.POST.get('Subtask')),phase=current_phase(),timestamp =datetime.now(),productivity=tot_prod)
            prod_stats.save()
            return redirect('ptv_stat')
        return render(request,'smt_smpo_dashboard/ptv_stat_update.html',{'qs':qs,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)})

def backfill_stat(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    if not ob:
        return redirect('login')
    else:
        xstat = ["YTS","WIP"]
        qs = brand_ops.objects.all().filter(bs_status__in=xstat)
        if request.POST:
            ob = brand_ops.objects.get(bid=str(request.POST.get('id')))
            ob.bs_status = str(request.POST.get('Subtask'))
            ob.save()

            no_keys,tot_prod,tt_prod = 0,0,0
            if ob.bs_status == "Ingestion completed" :
                ben_ob = benchmark.objects.filter(task="Backfill - DQ",subtask="Ingestion completed")
                for i in ben_ob:
                    mins = int(i.productivity)
                tot_prod = mins
            
            elif ob.bs_status == "Published" :
                ben_ob = benchmark.objects.filter(task="Backfill - DQ",subtask="Published")
                for i in ben_ob:
                    mins = int(i.productivity)
                tot_prod = mins

            elif ob.bs_status == "Publised with ion file" :
                ben_ob = benchmark.objects.filter(task="Backfill - Manual",subtask="Publised with ion file")
                for i in ben_ob:
                    mins = int(i.productivity)
                tot_prod = mins
            
            elif ob.bs_status == "NM completed" :
                od = brand_program.objects.get(bid=ob.bid)
                if od.keys_count <= 120 : no_keys = od.keys_count
                else : no_keys = 120

                if ob.backfill_type == "DQ" :
                    ben_ob = benchmark.objects.filter(task="Backfill - DQ",subtask="NM completed")
                    for i in ben_ob:
                        mins = int(i.productivity)
                    tot_prod = mins*no_keys

                elif ob.backfill_type == "Manual" :
                    ben_ob = benchmark.objects.filter(task="Backfill - Manual",subtask="NM completed")
                    for i in ben_ob:
                        mins = int(i.productivity)
                    tot_prod = mins*no_keys

            elif ob.bs_status == "BEM completed" :
                bem_attri = ob.bem_attribute_count
                if ob.backfill_type == "DQ" :
                    ben_ob = benchmark.objects.filter(task="Backfill - DQ",subtask="BEM completed")
                    for i in ben_ob:
                        mins = int(i.productivity)
                    tot_prod = mins*bem_attri

                elif ob.backfill_type == "Manual" :
                    ben_ob = benchmark.objects.filter(task="Backfill - Manual",subtask="BEM completed")
                    for i in ben_ob:
                        mins = int(i.productivity)
                    tot_prod = mins*bem_attri

            elif ob.bs_status == "VV completed" :
                attri_count = ob.backfill_pt_target_attributes_count
                attri_count_dq = (ob.backfill_pt_target_attributes_count/100)*40
                if ob.backfill_type == "DQ" :
                    ben_ob = benchmark.objects.filter(task="Backfill - DQ",subtask="VV completed")
                    for i in ben_ob:
                        mins = int(i.productivity)
                    tt_prod = mins*attri_count_dq
                    if ob.language == "Others" : tot_prod = tt_prod+30
                    else : tot_prod = tt_prod

                elif ob.backfill_type == "Manual" :
                    ben_ob = benchmark.objects.filter(task="Backfill - Manual",subtask="VV completed")
                    for i in ben_ob:
                        mins = int(i.productivity)
                    tt_prod = mins*attri_count
                    if ob.language == "Others" : tot_prod = tt_prod+30
                    else : tot_prod = tt_prod
                    

            exists_obj = productivity.objects.all().filter(website=ob.website,brand=ob.brand,user=user,task=str(request.POST.get('task')),sub_task=str(request.POST.get('Subtask')),phase__icontains=datetime.today().year).count()
            if exists_obj==0:
                prod_stats = productivity.objects.create(website=ob.website,brand=ob.brand,user=user,task=str(request.POST.get('task')),sub_task=str(request.POST.get('Subtask')),phase=current_phase(),timestamp =datetime.now(),productivity = tot_prod)
                prod_stats.save()
                return redirect('backfill_stat')
            else:
                prod_stats = productivity.objects.create(website=ob.website,brand=ob.brand,user=user,task=str(request.POST.get('task')),sub_task=str(request.POST.get('Subtask')),phase=current_phase(),timestamp =datetime.now(),productivity = int(0))
                prod_stats.save()
                return redirect('backfill_stat')
        return render(request,'smt_smpo_dashboard/backfill_stat_update.html',{'qs':qs,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)})


def bem_publish_stat(request):
    current_user = request.user
    user= current_user.username
    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    if not ob:
        return redirect('login')
    else:
        xstat = ["YTS","WIP"]
        qs = brand_ops.objects.all().filter(bs_status__in=xstat)
        if request.POST:
            ob = brand_ops.objects.get(bid=str(request.POST.get('id')))
            ob.bs_status = str(request.POST.get('Subtask'))
            ob.save()

            exists_obj = productivity.objects.all().filter(website=ob.website,brand=ob.brand,user=user,task=str(request.POST.get('task')),sub_task=str(request.POST.get('Subtask')),phase__icontains=datetime.today().year).count()
            value_productivity = benchmark.objects.get(task=str(request.POST.get('task')),subtask=str(request.POST.get('Subtask')))
            if exists_obj==0:
                prod_stats = productivity.objects.create(website=ob.website,brand=ob.brand,user=user,task=str(request.POST.get('task')),sub_task=str(request.POST.get('Subtask')),phase=current_phase(),timestamp =datetime.now(),productivity = int(value_productivity.productivity))
                prod_stats.save()
                return redirect('bem_publish_stat')
            else:
                prod_stats = Productivity.objects.create(website=ob.website,brand=ob.brand,user=user,task=str(request.POST.get('task')),sub_task=str(request.POST.get('Subtask')),phase=current_phase(),timestamp =datetime.now(),productivity = int(0))
                prod_stats.save()
                return redirect('bem_publish_stat')
        return render(request,'smt_smpo_dashboard/bem_publish_status.html',{'qs':qs,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)})

def bs_met(request):
    current_user = request.user
    user= current_user.username

    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    if not ob:
        return redirect('login')
    else:
        stat = ['YTS','WIP']
        obj = brand_ops.objects.all().filter(bs_status__in=stat)

        if request.POST:
            ob = brand_ops.objects.get(bid=str(request.POST.get('id')))
            ob.pt_not_found = str(request.POST.get('pt_not_found'))
            ob.bs_attributes = str(request.POST.get('bs_attributes'))
            ob.bs_comments = str(request.POST.get('bs_comments'))
            ob.bs_filename = str(request.POST.get('bs_filename'))
            ob.bs_path = str(request.POST.get('bs_path'))
            ob.save()

            return redirect('bs_stat')

        context = {'user':user,'obj':  obj,'role':get_role(user)}
        return render(request,'smt_smpo_dashboard/bs_met_update.html',context)
def bsv_met(request):
    current_user = request.user
    user= current_user.username

    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    if not ob:
        return redirect('login')
    else:
        stat = ['YTS','WIP']
        obj = brand_ops.objects.all().filter(bs_status__in=stat)

        if request.POST:
            ob = brand_ops.objects.get(bid=str(request.POST.get('id')))
            ob.bsv_pt_not_found = str(request.POST.get('bsv_pt_not_found'))
            ob.bsv_attributes = str(request.POST.get('bsv_attributes'))
            ob.bsv_comments = str(request.POST.get('bsv_comments'))
            ob.bsv_inaccurate_selection = str(request.POST.get('bsv_inaccurate_selection'))
            ob.bsv_sample_selection = str(request.POST.get('bsv_sample_selection'))
            ob.save()

            return redirect('bsv_met')

        context = {'user':user,'obj':  obj,'role':get_role(user)}
        return render(request,'smt_smpo_dashboard/bsv_met_update.html',context)

def ptc_met(request):
    current_user = request.user
    user= current_user.username

    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    if not ob:
        return redirect('login')
    else:
        stat = ['YTS','WIP']
        obj = brand_ops.objects.all().filter(bs_status__in=stat)

        if request.POST:
            ob = brand_ops.objects.get(bid=str(request.POST.get('id')))
            ob.ptc_selection_size = str(request.POST.get('ptc_selection_size'))
            ob.parent_count = str(request.POST.get('parent_count'))
            ob.bundle_count = str(request.POST.get('bundle_count'))
            ob.ptc_comments = str(request.POST.get('ptc_comments'))
            ob.ptc_status = str(request.POST.get('ptc_status'))
            ob.ptc_file_name = str(request.POST.get('ptc_file_name'))
            ob.ptc_path = str(request.POST.get('ptc_path'))
            ob.ptc_no_pt = str(request.POST.get('no_pt'))
            ob.distinct_title = str(request.POST.get('distinct_title'))
            ob.save()

            return redirect('ptc_met')

        context = {'user':user,'obj':  obj,'role':get_role(user)}
        return render(request,'smt_smpo_dashboard/ptc_met_update.html',context)

def ptv_met(request):
    current_user = request.user
    user= current_user.username

    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    if not ob:
        return redirect('login')
    else:
        stat = ['YTS','WIP']
        obj = brand_ops.objects.all().filter(bs_status__in=stat)

        if request.POST:
            ob = brand_ops.objects.get(bid=str(request.POST.get('id')))
            ob.ptv_selection_size = str(request.POST.get('ptv_selection_size'))
            ob.parent_count = str(request.POST.get('parent_count'))
            ob.bundle_count = str(request.POST.get('bundle_count'))
            ob.ptv_comments = str(request.POST.get('ptv_comments'))
            ob.ptv_status = str(request.POST.get('ptv_status'))
            ob.ptv_file_name = str(request.POST.get('ptv_file_name'))
            ob.ptv_inaccurate_selection = str(request.POST.get('ptv_inaccurate_selection'))
            ob.ptv_sample_selection = str(request.POST.get('ptv_sample_selection'))
            ob.no_pt = str(request.POST.get('no_pt'))
            ob.distinct_title = str(request.POST.get('distinct_title'))
            ob.save()

            return redirect('ptv_met')

        context = {'user':user,'obj':  obj,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
        return render(request,'smt_smpo_dashboard/ptv_met_update.html',context)

def backfill_met(request):
    current_user = request.user
    user= current_user.username

    today = datetime.today()
    obb =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    if not obb:
        return redirect('login')
    else:
        stat = ['YTS','WIP']
        obj = brand_ops.objects.all().filter(bs_status__in=stat)

        if request.POST:
            ob = brand_ops.objects.get(bid=str(request.POST.get('id')))
            ob.ptv_selection_size = str(request.POST.get('backfill_status'))
            ob.parent_count = str(request.POST.get('backfill_pt_count'))
            ob.bundle_count = str(request.POST.get('backfill_source_attributes_count'))
            ob.ptv_comments = str(request.POST.get('backfill_pt_target_attributes_count'))
            ob.ptv_status = str(request.POST.get('backfill_comments'))
            ob.save()

            return redirect('backfill_met')

        context = {'user':user,'obj':  obj,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
        return render(request,'smt_smpo_dashboard/backfill_met_update.html',context)

def bem_publish_met(request):
    current_user = request.user
    user= current_user.username

    today = datetime.today()
    ob =  productivity.objects.filter(brand="Login",user=user,timestamp__icontains=today.strftime("%Y-%m-%d"))
    if not ob:
        return redirect('login')
    else:
        stat = ['YTS','WIP']
        obj = brand_ops.objects.all().filter(bs_status__in=stat)

        if request.POST:
            ob = brand_ops.objects.get(bid=str(request.POST.get('id')))
            ob.require_ontology_attributes_prior_count = str(request.POST.get('require_ontology_attributes_prior_count'))
            ob.converted_ontology_count = str(request.POST.get('converted_ontology_count'))
            ob.require_ontology_attributes_post_count = str(request.POST.get('require_ontology_attributes_post_count'))
            ob.slots_backfilled_count = str(request.POST.get('slots_backfilled_count'))
            ob.bem_attempted = str(request.POST.get('bem_attempted'))
            ob.bem_converted = str(request.POST.get('bem_converted'))
            ob.bem_inaccurate_selection = str(request.POST.get('bem_inaccurate_selection'))
            ob.bem_sample_selection = str(request.POST.get('bem_sample_selection'))
            ob.bem_publish_comment = str(request.POST.get('bem_publish_comment'))
            ob.save()

            return redirect('bem_publish_met')

        context = {'user':user,'obj':  obj,'role':get_role(user),'sp_role1':get_sp_role1(user),'sp_role2':get_sp_role2(user)}
        return render(request,'smt_smpo_dashboard/bem_publish_met_update.html',context)

