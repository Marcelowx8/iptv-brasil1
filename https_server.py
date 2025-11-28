import http.server
import ssl

PORT = 8443

server_address = ("0.0.0.0", PORT)
handler = http.server.SimpleHTTPRequestHandler

httpd = http.server.HTTPServer(server_address, handler)

# Criar contexto SSL moderno
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="ssl/cert.pem", keyfile="ssl/key.pem")

# Envolver o socket com SSL
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print(f"Servidor HTTPS ativo em https://0.0.0.0:{PORT}")
httpd.serve_forever()
