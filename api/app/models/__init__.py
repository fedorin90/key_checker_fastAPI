from .base import Base

# Импортируй все модели, чтобы они зарегистрировались в Base.metadata
from .user import User
from .key import Key
from .ms_account import MSAccount
from .proxy import Proxy

