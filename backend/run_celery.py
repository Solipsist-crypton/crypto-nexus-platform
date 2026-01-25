# backend/run_celery.py
import sys
import os
import subprocess

def run_celery():
    """Запуск Celery worker на Windows"""
    print("🚀 ЗАПУСК CELERY WORKER...")
    print("=" * 50)
    
    # Встановлюємо шлях
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Команда для запуску Celery
    cmd = [
        sys.executable,  # Поточний Python
        "-m", "celery",
        "-A", "app.celery_app",  # Шлях до celery_app
        "worker",
        "--loglevel=info",
        "-P", "solo",  # Важливо для Windows (не використовує processes)
        "-B"  # Включити beat (періодичні завдання)
    ]
    
    print(f"💻 Команда: {' '.join(cmd)}")
    print("📝 Логи Celery (Ctrl+C для зупинки):")
    print("-" * 50)
    
    try:
        # Запускаємо Celery
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Celery зупинено")
    except Exception as e:
        print(f"❌ Помилка: {e}")

if __name__ == "__main__":
    run_celery()