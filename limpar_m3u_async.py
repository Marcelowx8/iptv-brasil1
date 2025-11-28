import os
import asyncio
import aiohttp
import re

INPUT_DIR = "./"
OUTPUT_FILE = "lista_unificada_limpa.m3u8"

# Limite de conexões simultâneas (não use mais que 300 no Android)
MAX_CONNECTIONS = 150
TIMEOUT = 3

semaphore = asyncio.Semaphore(MAX_CONNECTIONS)

def extrair_urls_m3u(conteudo):
    """Extrai URLs de um arquivo M3U/M3U8"""
    urls = set()
    linhas = conteudo.splitlines()
    for linha in linhas:
        linha = linha.strip()
        if linha.startswith("http://") or linha.startswith("https://"):
            urls.add(linha)
    return urls

async def testar_url(session, url):
    """Testa se a URL está online usando HEAD com timeout"""
    async with semaphore:
        try:
            async with session.head(url, timeout=TIMEOUT, allow_redirects=True) as resp:
                if resp.status < 400:
                    return url
        except:
            return None

async def processar_urls(urls):
    """Testa todas as URLs de forma assíncrona"""
    print(f"\n🔎 Testando {len(urls)} URLs (async)...\n")

    connector = aiohttp.TCPConnector(limit=MAX_CONNECTIONS, ssl=False)

    async with aiohttp.ClientSession(connector=connector) as session:
        tarefas = [testar_url(session, url) for url in urls]
        resultados = await asyncio.gather(*tarefas)

    return [r for r in resultados if r]

def ler_listas():
    print("📂 Lendo arquivos .m3u/.m3u8...\n")

    urls_total = set()

    for nome in os.listdir(INPUT_DIR):
        if nome.lower().endswith(".m3u") or nome.lower().endswith(".m3u8"):
            caminho = os.path.join(INPUT_DIR, nome)
            print(f"➡ Arquivo: {nome}")

            try:
                with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                    conteudo = f.read()
                urls = extrair_urls_m3u(conteudo)
                urls_total.update(urls)
            except Exception as e:
                print(f"⚠ Erro lendo {nome}: {e}")

    print(f"\n📌 Total de URLs coletadas (sem duplicadas): {len(urls_total)}\n")
    return urls_total

def salvar_saida(urls):
    print("\n💾 Salvando lista final limpa...\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for url in urls:
            f.write(f"#EXTINF:-1,{url}\n{url}\n")

    print(f"✅ Arquivo final salvo como: {OUTPUT_FILE}\n")

async def main():
    urls = ler_listas()
    urls_ok = await processar_urls(urls)
    
    print(f"\n✔ URLs válidas: {len(urls_ok)}")
    print(f"✖ URLs removidas: {len(urls) - len(urls_ok)}")
    
    salvar_saida(urls_ok)

if __name__ == "__main__":
    asyncio.run(main())
