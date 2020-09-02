import time
from functools import wraps
import os
import sys
import traceback
from types import MethodType,FunctionType
STDOUT = sys.stdout
#python setup.py sdist bdist_wheel 
#python -m twine upload dist/*



def writeFile(file_path, mode, content):
    with open(file_path, mode) as f:
        f.write(content + '\n')


def readFile(file_path):
    with open(file_path) as f:
        print(f.read())


def writeLog(msg, file_dir = os.path.dirname(__file__)):
    msg = str(msg)
    run_time = time.strftime( "%Y-%m-%d %H:%M:%S ", time.localtime())
    writeFile(os.path.join(file_dir, 'debug.log'), 'a', '%s %s' % (run_time, msg))
    print('%s %s' % (run_time, msg))


def failExsit(err, file_dir = os.path.dirname(__file__)):
    writeLog('[[ERROR]] : %s ' % err, file_dir)

# 让输出变为标准输出
def beStdOut():
    sys.stdout = STDOUT

# 让输出变为定制输出
def beCusOut(custom_out):
    sys.stdout = custom_out

class __BeautyLogOut__:
    def __init__(self, func_name, file_dir = os.path.dirname(__file__)):
        self._buff = ''
        self.func_name = func_name
        self.file_dir = file_dir

    def write(self, out_stream):
        if out_stream not in ['', '\r', '\n', '\r\n']: # 换行符不单独输出一行log
            self_out = sys.stdout
            beStdOut() # 设为标准输出
            writeLog("<%s> %s" % (self.func_name, out_stream), self.file_dir)
            beCusOut(self_out) # 设为定制输出

    def flush(self):
        self._buff = ""


def logDecoration(func):
    
    @wraps(func)
    def log(*args, **kwargs):
        try:
            file_dir = os.path.dirname(func.__code__.co_filename)
            caller_name = sys._getframe(1).f_code.co_name
            
            beStdOut() # 设为标准输出
            if caller_name != '<module>': # 若函数中调用了子函数，应打印调用者信息
                writeLog("<%s> is calling [%s]" % (caller_name, func.__name__), file_dir)
            # writeLog("<%s> is called" % func.__name__, file_dir)
            func_args = str(args)
            print(func_args)
            if isinstance(func,FunctionType):
                writeLog("<%s> is called as a function" % func.__name__, file_dir)
            else:
                writeLog("<%s> is called as a method" % func.__name__, file_dir)
                
            beCusOut( __BeautyLogOut__(func.__name__, file_dir)) # 设为定制输出
            func_return = str(func(*args, **kwargs))

            beStdOut() # 设为标准输出
            writeLog("<%s> return [%s]" % (func.__name__, func_return), file_dir)
            if caller_name != '<module>': # 若函数中调用了子函数，子函数退出时，定制输出应为主函数的定制输出
                beCusOut( __BeautyLogOut__(caller_name)) # 设为定制输出
            return func_return

        except Exception as err:
            beStdOut() # 设为标准输出
            failExsit("<%s> %s" % (func.__name__, err), file_dir)
            sys.exit(0)
    return log


class LogDecorationClass:
    def __init__(self):
        pass

    def __call__(self, func):
        @wraps(func)
        def log(*args, **kwargs):
            try:
                file_dir = os.path.dirname(func.__code__.co_filename)
                caller_name = sys._getframe(1).f_code.co_name
                
                beStdOut() # 设为标准输出
                if caller_name != '<module>': # 若函数中调用了子函数，应打印调用者信息
                    writeLog("<%s> is calling [%s]" % (caller_name, func.__name__), file_dir)
                writeLog("<%s> is called" % func.__name__, file_dir)

                beCusOut( __BeautyLogOut__(func.__name__)) # 设为定制输出
                func_return = str(func(*args, **kwargs))

                beStdOut() # 设为标准输出
                writeLog("<%s> return [%s]" % (func.__name__, func_return), file_dir)
                if caller_name != '<module>': # 若函数中调用了子函数，子函数退出时，定制输出应为主函数的定制输出
                    beCusOut( __BeautyLogOut__(caller_name)) # 设为定制输出
                return func_return

            except Exception as err:
                beStdOut() # 设为标准输出
                failExsit("<%s> %s" % (func.__name__, err), file_dir)
                sys.exit(0)
        return log
if __name__ == "__main__":

    @LogDecorationClass()
    def my():
        print('a')
        print('b')
        try:
            print('try')
            raise Exception("ERERERER")
        except Exception as err:
            print('except')
        
    @LogDecorationClass()
    def main():
        print('main1')
        my()
        print("main2")
        try:
            print('try')
            raise Exception("ERERERER")
        except Exception as err:
            print('except')
    main()
    class test:
        @logDecoration
        def m(self):
            print('main1')
            my()
            print("main2")
            try:
                print('try')
                raise Exception("ERERERER")
            except Exception as err:
                print('except')
    Test=test()
    Test.m()
    main()

