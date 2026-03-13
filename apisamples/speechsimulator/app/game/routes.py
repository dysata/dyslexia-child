from app.game import views    
from aiohttp import web


def setup_routes(app):
    app.router.add_get("/", views.index)
    app.router.add_get("/game1", views.game1)
    app.router.add_get("/game1d", views.game1d)
    app.router.add_get("/game2", views.game2)
    app.router.add_get("/game2d", views.game2d)
    app.router.add_get("/game3", views.game3)
    app.router.add_get("/game3f", views.game3f)
    app.router.add_get("/rrrex", views.rrrex)


    # перенести модель сюда
    app.router.add_post("/offer", views.offer)
    app.add_routes([web.get('/handle_new_phrase', views.handle_new_phrase)])
