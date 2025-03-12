import socket
import sounddevice as sd
import numpy as np
from cryptography.fernet import Fernet
import argparse
import time

# Генерация ключа (должен быть одинаковым на стороне отправителя и получателя)
key =  b'P3ihf_nJ-X6bwoq4SxLReEteehjHxg9HwBXZdbM-ZSE='  # Замените на реальный ключ
cipher = Fernet(key)

# Запись аудио
def record_audio(duration=15, sample_rate=44100):
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
def send_audio_data(ip, port, data, interval):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        chunk_size = 100  # Размер пакета (100 байт)
        total_size = len(data)
        sent_bytes = 0

        # Отправляем общий размер данных (первые 4 байта)
        size_bytes = total_size.to_bytes(4, byteorder='big')
        sock.sendto(cipher.encrypt(size_bytes), (ip, port))

        # Отправляем данные по частям
        while sent_bytes < total_size:
            chunk = data[sent_bytes:sent_bytes + chunk_size]
            encrypted_chunk = cipher.encrypt(chunk)  # Шифруем пакет
            sock.sendto(encrypted_chunk, (ip, port))
            sent_bytes += len(chunk)
            print(f"Отправлено {sent_bytes}/{total_size} байт")
            time.sleep(interval / 1000)  # Ждем указанный интервал

        print(f"Всего отправлено {total_size} байт на {ip}:{port}")
    except Exception as e:
        print(f"Ошибка при отправке данных: {e}")

if __name__ == "__main__":
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description="Отправка аудио по UDP")
    parser.add_argument("--ip", required=True, help="IP-адрес получателя")
    parser.add_argument("--port", type=int, default=65000, help="Порт получателя")
    parser.add_argument("--interval", type=int, default=100, help="Интервал обмена данными в миллисекундах")
    args = parser.parse_args()

    # Запись и отправка аудио
    audio_data = record_audio(duration=13)
    if audio_data:
        send_audio_data(args.ip, args.port, audio_data, args.interval)
    else:
        print("Не удалось записать аудио.")