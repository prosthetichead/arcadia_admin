from arcadia_admin import db, models

games = models.Game.query.all()
for g in games:
	print(g.name,g.file_name)