"""..."""
from dataclasses import dataclass
import sys
import requests
import json
import traceback
from typing import Generic, List, Union

# if __name__ == '__main__':
#     sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from .types.DataClass import DataClass, DataType
from .types.Null import Null
from .tools import pcformat
from .logu import logger

info, debug, warn, error = logger.info, logger.debug, logger.warning, logger.error


class NetManager(object):
    """网络请求功能简单封装
    """

    def __init__(self, session = None):
        if not session:
            self.sess = requests.session()
            self.sess.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'})
        
        else:
            self.sess = session

        info('sess inited.')

    def debug_log(self, response: requests.Response):
        """打印错误日志, 便于分析调试"""
        r = response.request
        warn(f'[method status_code] {r.method} {response.status_code}')
        warn(f'[url] {response.url}')
        warn(f'[headers] {r.headers}')
        warn(f'[request body] {r.body}')
        warn(f'[response body] {response.text[:200]}')

    def getData(self, url, *args, **kwargs):
        """封装网络请求
        my_fmt:
            str: 默认项
                my_str_encoding
            json:
                my_json_encoding
                my_json_loads
            bytes:
                None
            streaming:
                my_streaming_chunk_size
                my_streaming_cb
        """
        resp, data, ok = None, None, False
        method = kwargs.pop('method', 'GET')
        str_encoding = kwargs.pop('my_str_encoding', None)
        fmt: Union[str, Generic[DataType]] = kwargs.pop('my_fmt', 'str')
        streaming_chunk_size = kwargs.pop('my_streaming_chunk_size', 1024)
        streaming_cb = kwargs.pop('my_streaming_cb', None)
        max_try = kwargs.pop('my_retry', 1)

        for nr_try in range(max_try):
            try:
#-#                debug('url %s %s %s', url, pcformat(args), pcformat(kwargs))
                resp = self.sess.request(method, url, *args, **kwargs)
                if fmt == 'str':
                    try:
                        data = resp.text
                    except UnicodeDecodeError:
                        txt = resp.content
                        data = txt.decode(str_encoding, 'ignore')
                        warn('ignore decode error from %s', url)
#-#                    except ContentEncodingError:
                    except requests.exceptions.ContentDecodingError:
                        warn('ignore content encoding error from %s', url)
                elif fmt == 'json':
                    data = resp.json()
#-#                    if not data:
#-#                    if 'json' not in resp.headers.get('content-type', ''):
#-#                        warn('data not in json? %s', resp.headers.get('content-type', ''))
                elif fmt == 'bytes':
                    data = resp.content
                elif fmt == 'stream':
                    while 1:
                        chunk = resp.iter_content(streaming_chunk_size)
                        if not chunk:
                            break
                        streaming_cb(url, chunk)
                else:
                    data = self._result(resp, fmt)

                ok = True
                break
#-#            except aiohttp.errors.ServerDisconnectedError:
#-#                debug('%sServerDisconnectedError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
            except requests.exceptions.Timeout:
#-#                debug('%sTimeoutError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
                if nr_try == max_try - 1:  # 日志输出最后一次超时
                    debug('%sTimeoutError %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url)
            except requests.exceptions.ConnectionError:
                debug('%ConnectionError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
#-#            except aiohttp.errors.ClientResponseError:
#-#                debug('%sClientResponseError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
#-#            except ClientHttpProcessingError:
#-#                logger.opt(exception=True).debug('%sClientHttpProcessingError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
#-#            except ClientTimeoutError:
#-#                debug('%sClientTimeoutError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
            except requests.exceptions.ContentDecodingError:
                logger.opt(exception=True).debug('%sContentTypeError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
                data = resp.text(encoding=str_encoding)
                info('data %s', data[:50])
            except requests.exceptions.RequestException:
                logger.opt(exception=True).debug('%RequestException %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
            except UnicodeDecodeError:
                logger.opt(exception=True).debug('%sUnicodeDecodeError %s %s %s %s\n%s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs), pcformat(resp.headers), resp.read())
#-#                raise e
            except json.decoder.JSONDecodeError:
                logger.opt(exception=True).debug('%sJSONDecodeError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
            finally:
                pass

        return resp, data, ok

    def _result(self, response: requests.Response,
                dcls: Generic[DataType] = None,
                status_code: Union[List, int] = 200) -> Union[Null, DataType]:
        """统一处理响应
        :param response:
        :param dcls:
        :param status_code:
        :return:
        """
        if isinstance(status_code, int):
            status_code = [status_code]
        if response.status_code in status_code:
            text = response.text
            if dcls is not None:
                if not text.startswith('{'):
                    return dcls()
                try:
                    # noinspection PyProtectedMember
                    return DataClass._fill_attrs(dcls, json.loads(text))
                except TypeError:
                    self.debug_log(response)
                    error(dcls)
                    traceback.print_exc()

            return text

        warn(f'{response.status_code} {response.text[:200]}')
        return Null(response)

if __name__ == '__main__':

    @dataclass
    class ResponseType:
        origin: str

    try:
        net = NetManager()
        resp, data, ok = net.getData('http://httpbin.org/ip', timeout=10, my_fmt=ResponseType)
        info((resp, data, ok))
    except KeyboardInterrupt:
        info('cancel on KeyboardInterrupt..')
        sys.exit()
    finally:
        pass
