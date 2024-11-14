import os
import subprocess

FFMPEG_PATH = "ffmpeg.exe"
FFPLAY_PATH = "ffplay.exe"
# Definir o diretório base como o local onde o script está sendo executado
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DASH_OUTPUT_DIR = os.path.join(BASE_DIR, "dash_output")

def capture_video_audio():
    video_device = "Streaming Webcam"
    audio_device = "Microfone (Streaming Webcam MIC)"
    resolucao = "1920x1080"
    codec_video = "libx265"
    codec_audio = "aac"
    duracao = 3  # em minutos
    output_file = os.path.join(BASE_DIR, "captura_video.mp4")
    
    comando = [
        FFMPEG_PATH,
        "-f", "dshow",
        "-video_size", resolucao,
        "-i", f"video={video_device}:audio={audio_device}",
        "-c:v", codec_video,
        "-c:a", codec_audio,
        "-t", str(duracao * 60),
        output_file
    ]

    print(f"Executando comando: {' '.join(comando)}")
    subprocess.run(comando)

def transcode_video():
    input_file = os.path.join(BASE_DIR, "captura_video.mp4")
    output_file = os.path.join(BASE_DIR, "transcodificado_h264.mp4")
    
    comando = [FFMPEG_PATH, "-i", input_file, "-c:v", "libx264", output_file]
    print(f"Executando comando: {' '.join(comando)}")
    subprocess.run(comando)

def multiplex_dash():
    input_file = os.path.join(BASE_DIR, "transcodificado_h264.mp4")
    os.makedirs(DASH_OUTPUT_DIR, exist_ok=True)
    
    comando = [
        FFMPEG_PATH, "-i", "\"" + input_file + "\"", "-map", "0", 
        "-b:v:0", "3000k", "-s:v:0", "1920x1080",
        "-b:v:1", "1500k", "-s:v:1", "1280x720", 
        "-b:v:2", "800k", "-s:v:2", "640x480",
        "-b:a:0", "128k", "-ac:a:0", "2", 
        "-b:a:1", "64k", "-ac:a:1", "1",
        "-f", "dash", "\"" + os.path.join(DASH_OUTPUT_DIR, "manifest.mpd") + "\""
    ]
    
    print(f"Executando comando: {' '.join(comando)}")
    subprocess.run(comando)

def multiplex_mpeg_ts():
    input_file = os.path.join(BASE_DIR, "transcodificado_h264.mp4")
    output_file = os.path.join(BASE_DIR, "multiplexado.ts")
    
    comando = [FFMPEG_PATH, "-i", "\"" + input_file + "\"", "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", "-f", "mpegts", "\"" + output_file + "\""]
    print(f"Executando comando: {' '.join(comando)}")
    subprocess.run(comando)

def stream_dash():
    dash_manifest = os.path.join(DASH_OUTPUT_DIR, "manifest.mpd")
    comando = f"{FFMPEG_PATH} -f dash -i \"{dash_manifest}\" -c copy -f dash -listen 1 \"{dash_manifest}\""
    print(f"Executando comando: {comando}")
    subprocess.run(comando, shell=True)

def stream_rtp():
    rtp_output_video = "rtp://localhost:5004"
    rtp_output_audio = "rtp://localhost:5006"
    comando = [
        FFMPEG_PATH, "-re", "-i", "fixed_multiplexado.ts",
        "-map", "0:v", "-c:v", "copy", "-f", "rtp", rtp_output_video,
        "-map", "0:a", "-c:a", "aac", "-b:a", "128k", "-flags", "+global_header", "-f", "rtp", rtp_output_audio,
        "-sdp_file", "stream.sdp"
    ]
    print(f"Executando comando: {' '.join(comando)}")
    subprocess.run(comando)


def teste_dash():
    dash_manifest = os.path.join("dash_output\\", "manifest.mpd")
    comando = [FFPLAY_PATH, dash_manifest]
    print(f"Executando comando: {' '.join(comando)}")
    subprocess.run(comando, shell=True)

def teste_rtp():    
    comando = [FFPLAY_PATH, " -protocol_whitelist \"file,udp,rtp\" stream.sdp"]
    print(f"Executando comando: {' '.join(comando)}")
    subprocess.run(comando, shell=True)

def main():
    while True:
        print("/nMenu de Processamento Multimídia com FFmpeg")
        print("1. Capturar e Codificar Áudio e Vídeo")
        print("2. Transcodificar Vídeo")
        print("3. Multiplexar em DASH")
        print("4. Multiplexar em MPEG-2 TS")
        print("5. Iniciar Streaming DASH")
        print("6. Iniciar Streaming RTP")
        print("7. Testar DASH")
        print("8. Testar RTP")
        print("0. Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            capture_video_audio()
        elif escolha == '2':
            transcode_video()
        elif escolha == '3':
            multiplex_dash()
        elif escolha == '4':
            multiplex_mpeg_ts()
        elif escolha == '5':
            stream_dash()
        elif escolha == '6':
            stream_rtp()
        elif escolha == '7':
            teste_dash()
        elif escolha == '8':
            teste_rtp()
        elif escolha == '0':
            print("Encerrando o programa.")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
