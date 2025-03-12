import sounddevice as sd
import numpy as np
import socket
from cryptography.fernet import Fernet
import argparse

# Генерация ключа (должен быть одинаковым на стороне отправителя и получателя)
key = b'_6EXr4_WFeE4DGeX7sG0Hf2agh4afLhNks9xnDFStZw='  # Замените на реальный ключ
cipher = Fernet(key)

# Запись аудио
def record_audio(duration=5, sample_rate=44100):
    print("Запись началась...")
    try:
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()  # Ждем окончания записи
        print("Запись завершена.")
        return audio_data.tobytes()  # Преобразуем в байты
    except Exception as e:
        print(f"Ошибка при записи аудио: {e}")
        return None

# Отправка данных
def send_audio_data(ip, port, data):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        chunk_size = 1024  # Размер пакета (1 КБ)
        total_size = len(data)
        sent_bytes = 0

        # Отправляем данные по частям
        while sent_bytes < total_size:
            chunk = data[sent_bytes:sent_bytes + chunk_size]
            sock.sendto(chunk, (ip, port))
            sent_bytes += len(chunk)
            print(f"Отправлено {sent_bytes}/{total_size} байт")

        print(f"Всего отправлено {total_size} байт на {ip}:{port}")
    except Exception as e:
        print(f"Ошибка при отправке данных: {e}")

if __name__ == "__main__":
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description="Отправка аудио по UDP")
    parser.add_argument("--ip", required=True, help="IP-адрес получателя")
    parser.add_argument("--port", type=int, default=65000, help="Порт получателя")
    args = parser.parse_args()

    # Запись и отправка аудио
    audio_data = record_audio(duration=3)
    if audio_data:
        send_audio_data(args.ip, args.port, audio_data)
    else:
        print("Не удалось записать аудио.")