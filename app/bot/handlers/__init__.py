from aiogram import Router

from app.bot.handlers import admin, inline_invite, start, status

root_router = Router()
root_router.include_router(admin.router)
root_router.include_router(inline_invite.router)
root_router.include_router(start.router)
root_router.include_router(status.router)
