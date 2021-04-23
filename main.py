from ebooklib import epub
from soundEpubParsor import EbookParsor
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sys

# 파일명 치환
def convert_file_name(name, sep):
    __name = name
    for v in sep:
        if v == " " or v == "'":
            __name = __name.replace(v, "_")
        else:
            __name = __name.replace(v, "")

    __name = __name.replace("__", "_") # space("  ") 또는 dot(.)이 2개 인 경우 발생할 수 있으므로 예외 치환 추가.
    return __name

# 파싱한 epub 데이터를 파일로 저장
def epub_parsor_save_file(data, savePath):
    print("epub_parsor_save_file path : %s" %(savePath))
    f = open(savePath, "a")
    try:
        i = 0
        for v in data.synthesis_texts:
            index = "__sep__%d\n" %(i)
            f.write(index)
            f.write(v)
            i += 1
    except EOFError as error:
        print("end of files" %(savePath))
    except FileNotFoundError as error:
        print(error)
    except:
        return True
    finally:
        f.close()

    return False

# epub 파일 텍스트 추출
def extract_epub_text(file_path):
    try:
        book = epub.read_epub(file_path)
        ebook_parsor = EbookParsor()
        ebook_parsor.get_metadata_requires(book)
        ebook_parsor.get_content_items(book)
    except NameError as error:
        print(error)
    except IndexError as error:
        print(error)
    except:
        print("Unexpected error")
    finally:
        pass

    return ebook_parsor

class EpubParsorServer(BaseHTTPRequestHandler):

    __epub_parsor_save_file = ""
    __epub_title = ""
    __epub_replace_title = ""
    # __epub_creator = ""

    def do_POST(self):
        if self.path == "/epub-parsor":
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            jsonObject = json.loads(post_body)
            file_path = jsonObject.get('fullPath')
            save_path = jsonObject.get('savePath')
            print("file_path : ", file_path, ", save_path : ", save_path)

            # get epub texts
            epub_object = extract_epub_text(file_path)
            
            # save parsor file
            self.__epub_title = epub_object.title[0][0]
            self.__epub_replace_title = convert_file_name(epub_object.title[0][0], ["'","/", " ", "."])
            # if len(epub_object.creator) > 0: # In some case, there is no creator on book.
            #     self.__epub_creator = epub_object.creator[0][0]
            self.__epub_parsor_save_file = save_path + self.__epub_replace_title + ".txt"
            # print("title : ", self.__epub_replace_title, ", creator : ", self.__epub_creator, ", save_file : ",
            #  self.__epub_parsor_save_file)
            ret = epub_parsor_save_file(epub_object, self.__epub_parsor_save_file)
            if ret:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'fail'
                }, ensure_ascii=False).encode())
                return

            # rseponse
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'ok',
                'savePath': self.__epub_parsor_save_file,
                'title': self.__epub_title,
                # 'creator': self.__epub_creator
            }, ensure_ascii=False).encode())

            return

def main():
    '''
    - 설치
      $ pip install EbookLib
      $ pip3 install EbookLib
    '''
    print("start http web")
    hostName = '127.0.0.1'
    serverPort = 33113
    server = HTTPServer((hostName, serverPort), EpubParsorServer)
    print("Server start http://%s/%s" % (hostName, serverPort))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("server stop")

if __name__ == "__main__":
    main()