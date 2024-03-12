import os


class Settings:
    # jwt密钥
    SECRET_KEY = "hLfMUNxL07YQ2Orom6n+fUH6O1LDaVDb"
    # token过期时间
    TOKEN_EXPIRE_MINUTES = 15
    # token加密算法
    ALGORITHM = "HS256"


settings = Settings()