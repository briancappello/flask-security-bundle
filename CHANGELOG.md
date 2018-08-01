# CHANGELOG

## 0.4.0 (unreleased)

* automatically send the csrf token in the response cookie
* use the default behavior of controllers to name endpoints (in effect, rename the prefixes from `security` to `security_controller`)
* rename a translations keys for template h1 headings
* rename email templates and service methods for consistency
* move setting of the `csrf_token` cookie to flask unchained's controller bundle
* do not depend on `UserMixin`, `RoleMixin`, or `AnonymousUser` from flask_security
* do not depend on `current_user`, `login_user`, `logout_user`, `hash_password`, `get_hmac`, `user_double_hash`, `confirm_email_token_status`, and `reset_password_token_status` utility functions from flask_security
* refactor register form to always require password confirmation

## 0.3.0 (2018/07/25)

* update to flask unchained 0.5

## 0.2.1 (2018/07/17)

* fix missing import statement in validators.py
* fix inclusion of translation files in the distribution

## 0.2.0 (2018/07/16)

* upgrade to flask-unchained >= 0.3.1
* upgrade to flask-sqlalchemy-bundle >= 0.3.1
* add templates for security controller routes
* consolidate as much validation logic onto the user model as possible
* add translations support for form field labels, submit button labels, and error messages

## 0.1.2 (2018/05/01)

* alias `current_user` to the flask_security_bundle package
* fix emailing upon `change_password` action

## 0.1.1 (2018/04/22)

* depend on flask-mail-bundle

## 0.1.0 (2018/04/08)

* initial release
