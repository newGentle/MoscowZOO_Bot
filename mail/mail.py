import smtplib
import email.message


def send_mail(to_mail, from_mail, password, user, animal):
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()

    server.login(from_mail, password)

    msg = email.message.Message()
    msg['From'] = from_mail
    msg['To'] = to_mail
    msg['Subject'] = 'Новый потенциальный опекун.'

    string = open("mail/mail_template.html", "r", encoding="utf-8").read()
    parts = string.split("USERNAME")
    string = user.join(parts)
    parts = string.split("ANIMAL")
    string = animal.join(parts)

    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(string)

    server.sendmail(from_mail, to_mail, msg.as_string().encode("utf-8"))
    server.quit()
