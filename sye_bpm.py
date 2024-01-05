import re
import webbrowser
import traceback

from flowlauncher import FlowLauncher,FlowLauncherAPI
from subprocess import Popen

import sys,os
import qry_func as func

BASE_DIR=os.path.dirname(__file__)
sys.path.append(BASE_DIR)

webbrowser.register("ie",None,webbrowser.BackgroundBrowser(r"C:\Program Files\internet explorer\iexplore.exe"))
webbrowser.register("edge",None,webbrowser.BackgroundBrowser(r"D:\Documents\luo sheng he\Programs\Edge\msedge.exe"))

class Main(FlowLauncher):
    def query(self, param):
        params = re.split('\s+', param.strip())
        if len(params[0]) == 0:
            return []
        func_name = params[0].lower()
        if func_name in func.FUNCTION_NAMES:
            func_name = func.FUNCTION_NAMES[func_name]
        query_name = 'query_'+func_name
        query_data = ' '.join(params[1:])
        if hasattr(func, query_name):
            query_func = getattr(func, query_name)
            if hasattr(query_func, '__call__'):
                try:
                    results = query_func(query_data)
                except Exception:
                    FlowLauncherAPI.show_msg("Error", traceback.format_exc())
                    return []
                for result in results:
                    if 'ContextData' in result:
                        result['ContextData'] = func_name + \
                            '_'+result['ContextData']
                return results
        else:
            return []

    def context_menu(self, param):
        data = param.strip().split('_', 1)
        func_name, context_data = data[0], data[1]
        context_name = 'context_'+func_name
        result = []
        if hasattr(func, context_name):
            context_func = getattr(func, context_name)
            if hasattr(context_func, '__call__'):
                result = context_func(context_data)
        return result

    def open_url(self, url):
        webbrowser.open_new_tab(url)

    def open_ie_url(self, url):
        webbrowser.get('ie').open_new_tab(url)
        
    def open_edge_url(self, url):
        webbrowser.get('edge').open_new_tab(url)

    def __get_proxies(self):
        proxies = {}
        #if self.proxy and self.proxy.get("enabled") and self.proxy.get("server"):
        #    proxies["http"] = "http://{}:{}".format(
        #        self.proxy.get("server"), self.proxy.get("port"))
        #    proxies["https"] = "http://{}:{}".format(
        #        self.proxy.get("server"), self.proxy.get("port"))
        return proxies


if __name__ == '__main__':
    Main()
