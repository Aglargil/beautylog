import time
from functools import wraps
import os
import sys
import traceback
import _ctypes
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
            writeLog("[%s] %s" % (self.func_name, out_stream), self.file_dir)
            beCusOut(self_out) # 设为定制输出

    def flush(self):
        self._buff = ""


def logDecoration(func):

    @wraps(func)
    def log(*args, **kwargs):
        try:
            file_dir = os.path.dirname(func.__code__.co_filename)
            caller_name = sys._getframe(1).f_code.co_name
            # 判断是否为类内调用
            try:
                func_args = str(args[0]).strip('<>').split(' ')
                func_id = int(func_args[-1], 16) # 获取对象地址
                func_class = func_args[0].split('.')[-1]
                func_obj = _ctypes.PyObj_FromPtr(func_id) # 通过_ctypes的api进行对内存地址的对象
                func_obj_method = str(dir(func_obj))
            except:
                func_args = str(args)
                func_obj_method = [func.__name__]
            if func.__name__ in func_obj_method and 'object' in func_args: # 若为类内调用
                func_name = '<%s %s><%s>' % (func_class, func_id, func.__name__)
                caller_name = '<%s %s><%s>' % (func_class, func_id, caller_name)
            else:
                func_name = func.__name__

            beStdOut() # 设为标准输出
            if '<module>' not in caller_name: # 若函数中调用了子函数，应打印调用者信息
                writeLog("[%s] is calling [%s]" % (caller_name, func_name), file_dir)
            # writeLog("<%s> is called" % func.__name__, file_dir)

            beCusOut( __BeautyLogOut__(func_name, file_dir)) # 设为定制输出
            func_return = str(func(*args, **kwargs))

            beStdOut() # 设为标准输出
            writeLog("[%s] return [%s]" % (func_name, func_return), file_dir)
            if '<module>' not in caller_name: # 若函数中调用了子函数，子函数退出时，定制输出应为主函数的定制输出
                beCusOut( __BeautyLogOut__(caller_name)) # 设为定制输出
            return func_return

        except Exception as err:
            beStdOut() # 设为标准输出
            failExsit("<%s> %s" % (func_name, err), file_dir)
            sys.exit(0)
    return log

'''
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
                # writeLog("<%s> is called" % func.__name__, file_dir)

                try:
                    func_args = str(args[0]).strip('<>').split(' ')
                    func_id = int(func_args[-1], 16) # 获取对象地址
                    func_obj = _ctypes.PyObj_FromPtr(func_id) # 通过_ctypes的api进行对内存地址的对象
                    func_obj_method = str(dir(func_obj))
                except:
                    func_args = str(args)
                    func_obj_method = [func.__name__]
                if func.__name__ in func_obj_method and 'object' in func_args:
                    writeLog("<%s> is called as a method" % func.__name__, file_dir) 
                else:
                    writeLog("<%s> is called as a function" % func.__name__, file_dir)

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
'''
if __name__ == "__main__":

    @logDecoration
    def my():
        print('a')
        print('b')
        try:
            print('try')
            raise Exception("ERERERER")
        except Exception as err:
            print('except')

    @logDecoration
    def main(args):
        print('main1')
        my()
        print("main2")
        try:
            print('try')
            raise Exception("ERERERER")
        except Exception as err:
            print('except')
    class Test:
        @logDecoration
        def main(self):
            print('I\'m in the test_main')
        @logDecoration
        def main2(self):
            self.main()
            print('main2')
    test = Test()
    test.main2() # 调用类中方法
    print('this is the split line----------------------------')
    my() # 调用函数
    print('this is the split line----------------------------')
    main(test) # bug
