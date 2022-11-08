import django
django.setup()

from tos_web.models import Invitation
from tos_web.models import UserProfile
from tos_web.models import Verification
from tos_web.tasks import invitation_email
from tos_web.tasks import verification_email


user_emails = UserProfile.objects.values('email')

def send_invitations(dry=False):
    pending = Invitation.objects.exclude(
        email__in=user_emails
    )
    print('Pending invitations:', pending.count())
    if dry:
        return
    for p in pending:
        print(p.email, 'was queued!')
        invitation_email.delay(p.email)


def send_verifications(dry=False):
    pending = Verification.objects.filter(user__is_active=False)
    print('Pending verifications:', pending.count())
    if dry:
        return
    for p in pending:
        print(p.user.email, 'was queued!')
        verification_email(
            p.user.email,
            p.user.firstname.encode('utf-8'),
            p.token
        )


def main():
    send_invitations(dry=False)
    send_verifications(dry=False)


if __name__ == '__main__':
    main()
