from arcadia_admin import db, models

p = models.Platform(id='1', name='Super Nintendo')
db.session.add(p)
db.session.commit()