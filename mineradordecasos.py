import json
import yt_dlp

# Consultas otimizadas buscando direto os casos de maior audiência dos criadores
CANAIS_BUSCA = [
    {"nome": "Marcos Campos", "query": "Marcos Campos casos reais crimes"},
    {"nome": "Ju Cassini", "query": "Ju Cassini casos criminais investigação"},
    {"nome": "Ossos Perdidos", "query": "Ossos Perdidos casos reais crimes"}
]

# Régua ajustada: pega a partir de 1M para não perder os de 1M a 3.5M+
MINIMO_VIEWS = 1_000_000

def formatar_views(qtd: int) -> str:
    if qtd >= 1_000_000:
        return f"{qtd / 1_000_000:.2f}M visualizações"
    if qtd >= 1_000:
        return f"{qtd / 1_000:.0f}K visualizações"
    return f"{qtd} visualizações"

def minerar_top_casos(item: dict, max_resultados: int = 50):
    nome = item["nome"]
    termo = item["query"]
    print(f"\n[🔍] Buscando acervo viral de @{nome} (analisando até {max_resultados} vídeos)...")

    # ytsearch com ordenação por contagem de views na URL interna
    busca = f"ytsearch{max_resultados}:{termo}"

    ydl_opts = {
        'extract_flat': True,
        'dump_single_json': True,
        'quiet': True,
        'ignoreerrors': True,
        'no_warnings': True,
    }

    pautas_validas = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(busca, download=False)
            if not info:
                return pautas_validas

            entries = info.get('entries', [])
            for video in entries:
                if not video:
                    continue

                titulo = (video.get('title') or "").strip()
                canal_origem = video.get('channel') or video.get('uploader') or ""

                # Garante que o vídeo seja do criador ou diretamente relacionado a ele
                if nome.lower() not in canal_origem.lower() and nome.lower() not in titulo.lower():
                    continue

                views = video.get('view_count') or 0

                # Filtro de audiência
                if views < MINIMO_VIEWS:
                    continue

                video_id = video.get('id') or ""
                url_final = f"https://www.youtube.com/watch?v={video_id}" if video_id else video.get('url', '')

                pautas_validas.append({
                    "origem": nome,
                    "caso": titulo,
                    "views": views,
                    "views_formatado": formatar_views(views),
                    "url": url_final
                })

        except Exception as e:
            print(f"[!] Erro ao varrer @{nome}: {e}")

    return pautas_validas

def main():
    print("=== MINERADOR DE CASOS VIRAIS (AMPLIAÇÃO POR VIEWS) ===")
    todas_pautas = []
    links_vistos = set()

    for item in CANAIS_BUSCA:
        # Analisa até 50 vídeos por criador
        pautas = minerar_top_casos(item, max_resultados=50)
        
        # Remove duplicatas
        for p in pautas:
            if p["url"] not in links_vistos:
                links_vistos.add(p["url"])
                todas_pautas.append(p)

    # Ordena da maior audiência absoluta para a menor
    todas_pautas.sort(key=lambda x: x["views"], reverse=True)

    print(f"\n[+] Total de pautas virais únicas encontradas: {len(todas_pautas)}")

    # Salva o arquivo JSON
    with open("casos_minerados.json", "w", encoding="utf-8") as f:
        json.dump(todas_pautas, f, ensure_ascii=False, indent=2)

    # Gera a lista de pautas formatada
    with open("lista_de_pautas.txt", "w", encoding="utf-8") as f_out:
        for i, p in enumerate(todas_pautas, 1):
            f_out.write(f"RANKING #{i} | {p['views_formatado']}\n")
            f_out.write(f"CANAL: @{p['origem']}\n")
            f_out.write(f"CASO: {p['caso']}\n")
            f_out.write(f"LINK: {p['url']}\n")
            f_out.write("=" * 60 + "\n\n")

    print("[✔] 'casos_minerados.json' e 'lista_de_pautas.txt' atualizados com sucesso!")
    print("\n--- TOP CASOS MAIS ASSISTIDOS ---")
    for i, p in enumerate(todas_pautas[:10], 1):
        print(f"{i}º [{p['views_formatado']}] [@{p['origem']}] {p['caso']}")

if __name__ == "__main__":
    main()