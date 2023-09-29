new_user = """
<code>{user_id}</code> | @{username} зашёл в бота.
"""

existing_user = """
<code>{user_id}</code> | @{username} перезашёл в бота.
"""

access_given = """
<code>{user_id}</code> | @{username} выдана подписка
Уровень подписки: <b>{title}</b>
"""
access_zeroed = """
<code>{user_id}</code> | @{username} доступ обнулён
"""

subscription_expired = """
<code>{user_id}</code> | @{username} подписка истекла.
Уровень подписки: <b>{subscription_title}</b>
"""