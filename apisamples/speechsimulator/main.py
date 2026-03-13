from aiohttp import web  # основной модуль aiohttp
import jinja2  # шаблонизатор jinja2
import aiohttp_jinja2  # адаптация jinja2 к aiohttp

#from aiohttp_admin2 import setup_admin

import app.settings as settings

import ssl
import asyncio

import argparse
import os 
import logging


def setup_config(application):
    application["config"] = settings.config

# в этой функции производится настройка url-путей для всего приложения
def setup_routes(application):
    from app.game.routes import setup_routes
    setup_routes(application)  # настраиваем url-пути приложения game

def setup_external_libraries(application: web.Application) -> None:
    # указываем шаблонизатору, что html-шаблоны надо искать в папке templates
    aiohttp_jinja2.setup(application, loader=jinja2.FileSystemLoader("templates"))

async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in settings.pcs]
    await asyncio.gather(*coros)
    settings.pcs.clear()

def setup_app(application):  
    # настройка всего приложения состоит из:
    setup_config(application)
    setup_external_libraries(application)  # настройки внешних библиотек, например шаблонизатора
    setup_routes(application)  # настройки роутера приложения
#    setup_admin(application)
    app.on_shutdown.append(on_shutdown)
    app.router.add_static('/static/', path='static/', name='static')

@web.middleware
async def cache_control(request: web.Request, handler):
    response: web.Response = await handler(request)
#    resource_name = request.match_info.route.name
#    if resource_name and resource_name.startswith('static'):
    response.headers.setdefault('Cache-Control', 'no-cache')
    return response

app = web.Application(middlewares=[cache_control])

if __name__ == "__main__":  # эта строчка указывает, что данный файл можно запустить как скрипт

    settings.init_globals()
    with open(os.path.join(settings.ROOT, "text.txt"), 'w') as file:
        pass

    setup_app(app)  # настраиваем приложение
#    web.run_app(app)  # запускаем приложение
    web.run_app(
        app, access_log=None, host=settings.args.host, port=settings.config["common"]["port"], ssl_context=settings.ssl_context
    )
