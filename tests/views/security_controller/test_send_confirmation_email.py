import pytest


class TestResendConfirmation:
    def test_email_required(self, client, templates):
        r = client.post('security.send_confirmation')
        assert r.status_code == 200
        assert templates[0].template.name == \
               'security/send_confirmation_email.html'
        assert 'Email not provided' in r.html

    def test_cannot_reconfirm(self, user, client, templates):
        r = client.post('security.send_confirmation',
                        data=dict(email=user.email))
        assert r.status_code == 200
        assert templates[0].template.name == \
               'security/send_confirmation_email.html'
        assert 'Your email has already been confirmed.' in r.html

    @pytest.mark.options(SECURITY_CONFIRMABLE=True)
    def test_instructions_resent(self, client, outbox, templates,
                                 user_manager, security_service):
        # register a user
        user = user_manager.create(email='test@example.com',
                                   password='password')
        security_service.register_user(user)
        assert len(outbox) == len(templates) == 1
        assert templates[0].template.name == 'security/email/welcome.html'

        # have them request a new confirmation email
        r = client.post('security.send_confirmation',
                        data=dict(email=user.email))

        # make sure the get emailed a new confirmation token
        assert len(outbox) == 2
        assert len(templates) == 3
        assert templates[1].template.name == \
               'security/email/confirmation_instructions.html'
        assert templates[0].context.get('confirmation_link') != \
               templates[1].context.get('confirmation_link')

        # make sure the frontend tells them to check their email
        assert r.status_code == 200
        assert templates[2].template.name == \
               'security/send_confirmation_email.html'
        assert 'Confirmation instructions have been sent to test@example.com' in r.html
