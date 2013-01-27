import tornado
import tornado.httpserver
import tornado.websocket


class MainHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'Connected.'

    def on_message(self, message):
        self.write_message(message)


application = tornado.web.Application([
    (r'/', MainHandler),
])


server = tornado.httpserver.HTTPServer(application)


if __name__ == '__main__':
    server.listen(8888)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
