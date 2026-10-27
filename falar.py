import asyncio
import edge_tts

# O texto que você quer narrar
TEXTO = "As imagens de uma câmara de segurança revelaram o momento exato de um dos crimes mais chocantes do país."
# Voz padrão para documentários/crime (pode testar pt-BR-FranciscaNeural se quiser voz feminina)
VOICE = "pt-BR-AntonioNeural" 
OUTPUT_FILE = "narracao.mp3"

async def gerar_audio() -> None:
    communicate = edge_tts.Communicate(TEXTO, VOICE)
    await communicate.save(OUTPUT_FILE)
    print(f"[+] Áudio gerado com sucesso em: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(gerar_audio())