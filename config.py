import os
from dotenv import load_dotenv

load_dotenv() # Esto cargará variables desde un archivo .env si lo tienes

class Config:
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xyjtjaxbsrwksrudghww.supabase.co")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_b9UZUMecprvBdYyqpH83IQ_zv6mAOKY")
    PORT = 5000
    DEBUG = True