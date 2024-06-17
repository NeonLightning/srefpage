from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile='/etc/letsencrypt/live/srefs.damnserver.com/cert.pem', keyfile='/etc/letsencrypt/live/srefs.damnserver.com/privkey.pem')
httpd = HTTPServer(('0.0.0.0', 443), SimpleHTTPRequestHandler)
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
print("Serving at https://sref.damnserver.com:443/")
httpd.serve_forever()
