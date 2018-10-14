import os
import time
import shutil
import mimetypes
import argparse
import json
import http.server
import urllib
from pathlib import Path
from collections import defaultdict

from .template import script, header


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def _get_item_list(self, path, recursive=False):
        assert path.is_dir()
        items = []
        dir_path = "**/" if recursive else ""
        for ext in ['mp4', 'jpg', 'png', 'gif', 'jpeg']:
            items.extend([str(f) for f in path.glob('%s*.%s' % (dir_path, ext))])
        items.sort()
        return items

    def do_POST(self):
        data_string = self.rfile.read(int(self.headers.get('content-length')))
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Retrieve video and image files in dir_path
        dir_path = data_string.decode('utf-8')
        items = self._get_item_list(Path(dir_path))

        return_info = []
        for item_path in items:
            item_name = item_path.rsplit('/', 1)[-1]
            mod_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                     time.localtime(os.path.getmtime(item_path)))
            return_info.append({'name': item_name,
                                'path': item_path,
                                'time': mod_time})
        return_string = json.dumps(return_info).encode('utf-8')
        self.wfile.write(return_string)

    def do_GET(self):
        if self.path == '/':
            # Retrieve video and image files recursively
            items = self._get_item_list(Path(self._logdir), recursive=self._recursive)

            # Group files based on the parent dirs
            item_names = defaultdict(list)
            for item_path in items:
                if len(item_path.rsplit('/', 1)) > 1:
                    dir_name, item_name = item_path.rsplit('/', 1)
                else:
                    dir_name = ''
                    item_name = item_path
                item_names[dir_name].append((item_path, item_name))

            # Build a html file
            head_html = header.replace('max-height: 320px;',
                                       'max-height: {}px;'.format(self._max_height))
            head_html = head_html.replace('max-width: 320px;',
                                          'max-width: {}px;'.format(self._max_width))
            script_html = script.replace('max_length = 30',
                                         'max_length = {}'.format(self._max_file_name_length))
            if not self._display:
                script_html = script_html.replace('+ itemHTML', '+ ""')

            html = ['<!DOCTYPE html>', '<html>', head_html, '<body>']
            for dir_name in sorted(item_names.keys()):
                html += ['<button class="accordion">', dir_name,
                         '[%d items]' % len(item_names[dir_name]), '</button>',
                         '<div class="panel">', '</div>']
            html += [script_html, '</body>', '</html>']

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write('\n'.join(html).encode())
        else:
            # Send a raw file (video or image)
            f = self._send_head()
            if f:
                shutil.copyfileobj(f, self.wfile)
                f.close()

    # Code from https://gist.github.com/UniIsland/3346170
    def _send_head(self):
        """Common code for GET and HEAD commands.
        This sends the response code and MIME headers.
        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.
        """
        path = urllib.parse.unquote(os.getcwd() + self.path)
        f = None
        ctype = self.extensions_map['']
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    # Initialize extension maps
    if not mimetypes.inited:
        mimetypes.init() # Try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({'': 'application/octet-stream'})


def str2bool(v):
    return v.lower() == 'true'

def main():
    parser = argparse.ArgumentParser(
        prog='videoboard',
        description='A simple http server for visualizing videos and images',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--port', type=int, default=8000,
                        help='port number.')
    parser.add_argument('--logdir', type=str, default='.',
                        help='directory where videoboard '
                             'will look for videos and images.')
    parser.add_argument('--height', type=int, default=320,
                        help='maximum height of image/video.')
    parser.add_argument('--width', type=int, default=320,
                        help='maximum width of image/video.')
    parser.add_argument('--file_name_length', type=int, default=30,
                        help='maximum length of file name.')
    parser.add_argument('--recursive', type=str2bool, default=True,
                        choices=[True, False],
                        help='search files recursively.')
    parser.add_argument('--display', type=str2bool, default=True,
                        choices=[True, False],
                        help='display videos and images.')

    args = parser.parse_args()

    # Change directory to prevent access to directories other than logdir
    os.chdir(args.logdir)

    class RequestHandlerWithArgs(RequestHandler):
        _logdir = '.'
        _max_height = args.height
        _max_width = args.width
        _max_file_name_length = args.file_name_length
        _recursive = args.recursive
        _display = args.display

    server = http.server.HTTPServer(('', args.port), RequestHandlerWithArgs)

    try:
        print('Run videoboard server on port %d' % args.port)
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    print('Close server')
    server.server_close()


if __name__ == '__main__':
    main()
