from celery.task import task

from utils import send_templated_email


@task
def send_templated_email_async(to, subject, body_template, body_dict,
                               from_email=None, ct="html", fail_silently=False,
                               check_user_preference=True):
    return send_templated_email(
        to,subject, body_template, body_dict, from_email=None, ct="html",
        fail_silently=False, check_user_preference=check_user_preference)


@periodic_task(run_every=crontab(minute=0, hour=1))
def send_error_report(date=None):
    date = date or datetime.datetime.now() - datetime.timedelta(days=1)
    recipients = getattr(settings,'SEND_ERROR_REPORT_TO', None)
    if not recipients:
        return 
    data = errorreport._error_report_data(date)
    message = render_to_string("internal/error-report.txt", data)
    subject = date.strftime("Errors for Amara for %Y/%M/%d")
    send_mail(subject, message, "unisubs error bot", recipients)
