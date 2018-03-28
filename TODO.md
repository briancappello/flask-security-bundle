## documentation

# clean up the hash_password bullshit sprinkled throughout flask_security

* implement improvements from https://news.ycombinator.com/item?id=16356397 and http://habitatchronicles.com/2008/10/the-tripartite-identity-pattern/
    > refactor concept of user identities (well really, it more just needs implementing because flask-security has a complete shit concept of user identities)
    > improve email uniqueness checks (unicode)
    > add system for restricting usernames/emails

* implement `user` and `role` cli commands

* integrate with flask-jwt-extended (replace Flask-Security's token shit)

* integrate with flask-dance (for OAuth)

* figure out a better solution to sending emails

* figure out a robust solution to handling i18n in flask-unchained

* move all utility code that a user might want to customize into services

* move all settings defaults from the ext into the config module

* refactor the security extension so it doesn't use the all of its PITA setattr/getattr un-comprehensible magic
