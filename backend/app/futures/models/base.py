from sqlalchemy.ext.declarative import declarative_base

# Створюємо ОКРЕМИЙ Base для ф'ючерсів
# Це гарантує, що ми не зламаємо існуючі моделі
FuturesBase = declarative_base()