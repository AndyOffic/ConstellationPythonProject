import socket
import sounddevice as sd
import numpy as np
from cryptography.fernet import Fernet
import argparse

# Генерация ключа (должен быть одинаковым на стороне отправителя и получателя)
key =  b'_6EXr4_WFeE4DGeX7sG0Hf2agh4afLhNks9xnDFStZw='  # Замените на реальный ключ
cipher = Fernet(key)

# Воспроизведение аудио
def play_audio(audio_data, sample_rate=44100):
    print("Воспроизведение...")
    audio_array = np.frombuffer(audio_data, dtype=np.float32)
    sd.play(audio_array, sample_rate)
    sd.wait()
    print("Воспроизведение завершено.")

# Прием данных
def receive_audio_data(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    print(f"Ожидание данных на порту {port}...")

    # Буфер для сбора данных
    received_data = b""
    while True:
        chunk, addr = sock.recvfrom(1024)  # Получаем пакет
        received_data += chunk
        print(f"Получено {len(received_data)} байт от {addr}")

        # Если пакет меньше 1024 байт, это последний пакет
        if len(chunk) < 1024:
            break

    return received_data

if __name__ == "__main__":
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description="Прием аудио по UDP")
    parser.add_argument("--port", type=int, default=65000, help="Порт для приема данных")
    args = parser.parse_args()

    # Прием и воспроизведение аудио
    received_data = receive_audio_data(args.port)
    play_audio(received_data)