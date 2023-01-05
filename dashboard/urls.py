from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    url(r'^$', views.welcome_page,name='welcome_page'),
    url(r'^login_form/$', views.user_login, name='login'),
    url(r'^members$',views.members_view,name='members'),
    url(r'^rda/$', views.log_rda, name='rda'),
    url(r'^adhoc_form$',views.adhoc_form,name='adhoc_form'),
    url(r'^manager$', views.manager,name='manager'),
    url(r'^master$', views.master,name='master'),
    url(r'^approve_adhoc$',views.approve_adhoc,name='approve_adhoc'),
    url(r'^hist_adhoc$', views.hist_adhoc,name='hist_adhoc'),
    url(r'^audit$',views.auditor,name='auditor'),
    url(r'^attendence$', views.attendence,name='attendence'),
    url(r'^log_atten$', views.log_atten,name='log_atten'),
    url(r'^leave_planner$', views.leave_planner,name='leave_planner'),
    url(r'^view_db$',views.view_db,name='view_db'),
    url(r'^view_db2$',views.view_db2,name='view_db2'),
    url(r'^user_role$',views.user_role,name='user_role'),
    url(r'^usr_pro$', views.usr_pro,name='usr_pro'),
    url(r'^daily_cost$', views.daily_cost,name='daily_cost'),
    url(r'^monthly_cost$', views.monthly_cost,name='monthly_cost'),
    url(r'^assos_details$', views.assos_details,name='assos_details'),
    url(r'^productivity_edit$', views.productivity_edit,name='productivity_edit'),
    url(r'^producitvity_table$', views.producitvity_table,name='producitvity_table'),
    url(r'^main_prod$',views.main_prod,name='main_prod'),
    url(r'^crawl_r$', views.crawl_r,name='crawl_r'),
    url(r'^lead$',views.lead,name='lead'),
    url(r'^aud_cost$', views.aud_cost,name='aud_cost'),
    url(r'^sme_cost$', views.sme_cost,name='sme_cost'),
    url(r'^eod_summary$', views.eod_summary,name='eod_summary'),
    url(r'^allocate_wb$', views.allocate_wb,name='allocate_wb'),
    url(r'^scrape_update$', views.scrape_update,name='scrape_update'),
    url(r'^backfill_request$', views.backfill_request,name='backfill_request'),
    url(r'^matching_status$', views.matching_status,name='matching_status'),
    url(r'^incremental_status$', views.incremental_status,name='incremental_status'),
    url(r'^update_identity_datapoints$', views.update_identity_datapoints,name='update_identity_datapoints'),
    url(r'^component_update$', views.component_update,name='component_update'),
    url(r'^update_business_usecase$', views.update_business_usecase,name='update_business_usecase'),
    url(r'^update_funnel_details$', views.update_funnel_details,name='update_funnel_details'),
    url(r'^update_e2e_funnel_details$', views.update_e2e_funnel_details,name='update_e2e_funnel_details'),
    url(r'^bs_alloc$', views.bs_alloc,name='bs_alloc'),
    url(r'^bsv_alloc$', views.bsv_alloc,name='bsv_alloc'),
    url(r'^ptv_alloc$', views.ptv_alloc,name='ptv_alloc'),
    url(r'^bem_alloc$', views.bem_alloc,name='bem_alloc'),
    url(r'^ptc_alloc$', views.ptc_alloc,name='ptc_alloc'),
    url(r'^backfill_alloc$', views.backfill_alloc,name='backfill_alloc'),
    url(r'^bs_realloc$', views.bs_realloc,name='bs_realloc'),
    url(r'^bsv_realloc$', views.bsv_realloc,name='bsv_realloc'),
    url(r'^ptc_realloc$', views.ptc_realloc,name='ptc_realloc'),
    url(r'^ptv_realloc$', views.ptv_realloc,name='ptv_realloc'),
    url(r'^bem_realloc$', views.bem_realloc,name='bem_realloc'),
    url(r'^publish_realloc$', views.publish_realloc,name='publish_realloc'),
    url(r'^backfill_realloc$', views.backfill_realloc,name='backfill_realloc'),
    url(r'^core$', views.core,name='core'),
    url(r'^sme$', views.sme,name='sme'),
    url(r'^stakeholder$', views.stakeholder,name='stakeholder'),
    url(r'^logout$',views.logout_view,name='logout'),
    url(r'^tt_update$',views.tt_update,name='tt_update'),
    url(r'^bnchmrk$',views.bnchmrk,name='benchmark'),
    url(r'^quality$',views.quality,name='quality'),
    url(r'^error_log$',views.error_log,name='error_log'),
    url(r'^view_planner$',views.view_planner,name='view_planner'),
    url(r'^allocate_wb2$',views.allocate_wb2,name='allocate_wb2'),
    url(r'^update_wid$',views.update_wid,name='update_wid'),
    url(r'^brand_ops_edit$',views.brand_ops_edit,name='brand_ops_edit'),
    url(r'^brand_prog_edit$',views.brand_prog_edit,name='brand_prog_edit'),
    url(r'^benchmark_edit$',views.benchmark_edit,name='benchmark_edit'),
    url(r'^prod_edit$',views.prod_edit,name='prod_edit'),
    url(r'^sod_summary$',views.sod_summary,name='sod_summary'),
    url(r'^backfill_ops_summary$',views.backfill_ops_summary,name='backfill_ops_summary'),
    url(r'^rampup_table$',views.rampup_table,name='rampup_table'),
    url(r'^eod_update$',views.eod_update,name='eod_update'),
    url(r'^bs_stat$',views.bs_stat,name='bs_stat'),
    url(r'^bsv_stat$',views.bsv_stat,name='bsv_stat'),
    url(r'^ptc_stat$',views.ptc_stat,name='ptc_stat'),
    url(r'^ptv_stat$',views.ptv_stat,name='ptv_stat'),
    url(r'^backfill_stat$',views.backfill_stat,name='backfill_stat'),
    url(r'^bem_publish_stat$',views.bem_publish_stat,name='bem_publish_stat'),
    url(r'^bs_met$',views.bs_met,name='bs_met'),
    url(r'^bsv_met$',views.bsv_met,name='bsv_met'),
    url(r'^ptc_met$',views.ptc_met,name='ptc_met'),
    url(r'^ptv_met$',views.ptv_met,name='ptv_met'),
    url(r'^backfill_met$',views.backfill_met,name='backfill_met'),
    url(r'^bem_publish_met$',views.bem_publish_met,name='bem_publish_met'),
    #url(r'^sod_eod$',views.sod_eod,name='sod_eod'),
    ]