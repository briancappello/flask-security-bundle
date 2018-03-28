## documentation

* implement improvements from https://news.ycombinator.com/item?id=16356397 and http://habitatchronicles.com/2008/10/the-tripartite-identity-pattern/
    > refactor concept of user identities (well really, it more just needs implementing because flask-security has a complete shit concept of user identities)
    > improve email uniqueness checks (unicode)
    > add system for restricting usernames/emails

* implement `user` and `role` cli commands

* integrate with flask-jwt-extended (replace Flask-Security's token shit)

* integrate with flask-dance (for OAuth)

* figure out a better solution to sending emails

#### and maybe the ultimate goal, stop depending on flask-security altogether

* requires a robust solution to handling i18n in flask-unchained
* move all utility code into services
* remove the datastore abstraction layer
* move all settings defaults from the ext into the config module
* ideally, shouldn't need the security ext at all. it doesn't do anything useful
* migrate tests from flask-security
