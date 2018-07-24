## documentation

* implement improvements from https://news.ycombinator.com/item?id=16356397 and http://habitatchronicles.com/2008/10/the-tripartite-identity-pattern/
    > refactor concept of user identities (well really, it more just needs implementing because flask-security has a complete shit concept of user identities)
    > improve email uniqueness checks (unicode)
    > add system for restricting usernames/emails

* implement `user` and `role` cli commands

* integrate with flask-jwt-extended (replace Flask-Security's token shit)

* integrate with flask-dance (for OAuth)

* move all utility code that a user might want to customize into services

* test SECURITY_TRACKABLE
