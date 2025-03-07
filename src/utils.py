from database import get_user_by_telegram_id


def validation_on_admin(telegram_id: int) -> bool:
    user = get_user_by_telegram_id(telegram_id=telegram_id)
    
    return user['admin'] == True
