import os
import socket
import traceback
from datetime import datetime


class WebServer:
    """
    Webサーバーを表すクラス
    """

    # 実行ファイルのあるディレクトリ
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # 静的配信するファイルを置くディレクトリ
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

    MIME_TYPES = {
       "html": "text/html",
       "css": "text/css",
       "png": "image/png",
       "jpg": "image/jpg",
       "gif": "image/gif",
    }

    def serve(self):
        """
        サーバーを起動する
        """

        print("=== サーバーを起動します ===")

        try:
            # socketを生成
            server_socket = socket.socket()
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # socketをlocalhostのポート8080番に割り当てる
            server_socket.bind(("localhost", 8081))
            server_socket.listen(10)

            while True:
                try:
                    # 外部からの接続を待ち、接続があったらコネクションを確立する
                    print("=== クライアントからの接続を待ちます ===")
                    (client_socket, address) = server_socket.accept()
                    print(f"=== クライアントとの接続が完了しました remote_address: {address} ===")

                    # クライアントから送られてきたデータを取得する
                    request = client_socket.recv(4096)

                    # クライアントから送られてきたデータをファイルに書き出す
                    with open("server_recv.txt", "wb") as f:
                        f.write(request)

                    # リクエスト全体を
                    # 1. リクエストライン(1行目)
                    # 2. リクエストヘッダー(2行目〜空行)
                    # 3. リクエストボディ(空行〜)
                    # にパースする
                    request_line, remain = request.split(b"\r\n", maxsplit=1)
                    request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)

                    # リクエストラインをパースする
                    method, path, http_version = request_line.decode().split(" ")

                    # pathの先頭の/を削除し、相対パスにしておく
                    relative_path = path.lstrip("/")
                    if relative_path == "":
                        relative_path = "index.html"
                    # ファイルのpathを取得
                    static_file_path = os.path.join(self.STATIC_ROOT, relative_path)
                    # print(static_file_path)
                    #   ~/workspace/python/httpd-serve/study/static/logo.png
                    # static_file_path = "static/index.html"

                    # ファイルからレスポンスボディを生成
                    if os.path.exists(static_file_path):
                        with open(static_file_path, "rb") as f:
                            response_body = f.read()
                        # レスポンスラインを生成
                        response_line = "HTTP/1.1 200 OK\r\n"

                        ext = os.path.splitext(static_file_path)[1][1:]
                        content_type = self.MIME_TYPES.get(ext, "application/octet-stream")
                    else:
                        # ファイルが見つからなかった場合は404を返す
                        response_body = "<html><body><h1>404 Not Found</h1></body></html>"
                        response_line = "HTTP/1.1 404 Not Found\r\n"
                        content_type = "text/html"


                    # レスポンスヘッダーを生成
                    response_header = ""
                    response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
                    response_header += "Host: HenaServer/0.1\r\n"
                    response_header += f"Content-Length: {len(response_body)}\r\n"
                    response_header += "Connection: Close\r\n"
                    response_header += f"Content-Type: {content_type}\r\n"

                    # レスポンス全体を生成する
                    response = (response_line + response_header + "\r\n").encode() + response_body

                    # クライアントへレスポンスを送信する
                    client_socket.send(response)

                except Exception:
                    print("=== リクエストの処理中にエラーが発生しました ===")
                    traceback.print_exc()

                finally:
                    client_socket.close()

        except Exception:
            print("=== サーバーの起動中にエラーが発生しました ===")
            traceback.print_exc()

        finally:
            print("=== サーバーを停止します。 ===")


if __name__ == "__main__":
    server = WebServer()
    server.serve()
