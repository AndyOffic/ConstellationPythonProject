import socket
import sounddevice as sd
import numpy as np
from cryptography.fernet import Fernet
import argparse
import time

# Генерация ключа (должен быть одинаковым на стороне отправителя и получателя)
key =  b'P3ihf_nJ-X6bwoq4SxLReEteehjHxg9HwBXZdbM-ZSE='  # Замена на реальный ключ
cipher = Fernet(key)

# Воспроизведение аудио
def play_audio(audio_data, sample_rate=44100):
    print("Воспроизведение...")
    try:
        # Проверяем, что размер данных кратен 4 байтам
        if len(audio_data) % 4 != 0:
            print("Ошибка: размер данных не кратен 4 байтам. Данные могут быть повреждены.")
            return

        audio_array = np.frombuffer(audio_data, dtype=np.float32)
        sd.play(audio_array, sample_rate)
        sd.wait()
        print("Воспроизведение завершено.")
    except Exception as e:
        print(f"Ошибка при воспроизведении аудио: {e}")

# Прием данных
def receive_audio_data(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    print(f"Ожидание данных на порту {port}...")

    # Буфер для сбора данных
    received_data = b""
    start_time = time.time()
    expected_size = None  # Ожидаемый размер данных

    while True:
        chunk, addr = sock.recvfrom(1024)  # Получаем пакет
        try:
            decrypted_chunk = cipher.decrypt(chunk)  # Расшифровываем пакет
        except Exception as e:
            print(f"Ошибка при дешифровании данных: {e}")
            continue

        # Если это первый пакет, извлекаем ожидаемый размер данных
        if expected_size is None:
            expected_size = int.from_bytes(decrypted_chunk[:4], byteorder='big')
            received_data += decrypted_chunk[4:]  # Пропускаем первые 4 байта (размер)
        else:
            received_data += decrypted_chunk

        print(f"Получено {len(received_data)}/{expected_size} байт от {addr}")

        # Если получены все данные, завершаем цикл
        if len(received_data) >= expected_size:
            break

    end_time = time.time()
    speed = (len(received_data) * 8) / (end_time - start_time) / 1024  # Скорость в Кбит/с
    print(f"Скорость приема: {speed:.2f} Кбит/с")

    return received_data[:expected_size]  # Обрезаем лишние данные

if __name__ == "__main__":
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description="Прием аудио по UDP")
    parser.add_argument("--port", type=int, default=65000, help="Порт для приема данных")
    args = parser.parse_args()

    # Прием и воспроизведение аудио
    received_data = receive_audio_data(args.port)
    play_audio(received_data)
