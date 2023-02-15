#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os,re,random
from utils.functions        import *

# 部分源码在反编译之后会出现package包名不正确的情况进行修复
def clearPackage(java_files):
    error_packages = {
        b"package BOOT-INF.classes.": b"package ",
        b"package WEB-INF.classes.": b"package ",
        b"package WEB-INF.classes;": b"",
        b"package BOOT-INF.classes;": b"",
        b"package src.main.java.": b"package ",
    }
    for java_file in java_files:
        if not os.path.isfile(java_file):
            continue
        error_flag = False
        content = ""
        with open(java_file, 'rb') as r:
            content = r.read()
            for error_package in error_packages.keys():
                if error_package in content:
                    content = content.replace(error_package, error_packages[error_package])
                    error_flag = True
        if error_flag:
            with open(java_file, 'wb') as w:
                w.write(content)

# 修复部分反编译之后的字段名称无初始化定义，eg:LineInputStream lineInputStream;
def repairNoneDeclare(java_files):
    for java_file in java_files:
        if not os.path.isfile(java_file):
            continue
        error_flag = False
        content = ""
        with open(java_file, 'rb') as r:
            content = r.read()
            imports = re.compile(rb"import (?:\w+\.)+(\w+)").findall(content)
            for delaration in re.compile(rb'\s*(\w+)\s+\w+\s*;').findall(content):
                black_list = ['return', 'int', 'char', 'boolean', 'String', 'throw', 'float', ]
                if delaration != "" and delaration not in black_list and delaration in imports:
                    content = re.compile(b'(\\s*' + delaration + b'\\s+\\w+\\s*);').sub(rb'\1' + b' = null;', content)
                    error_flag = True
        
        if error_flag:
            with open(java_file, 'wb') as w:
                w.write(content)

# 修复混淆代码中方法和属性为关键字的情况
def repairKeyPrivateFunction(java_files):
    java_keys = b"abstract,assert,boolean,break,byte,case,catch,char,class,const,continue,\
    default,do,double,else,enum,extends,final,finally,float,for,goto,if,implements,import,\
    instanceof,int,interface,long,native,new,package,private,protected,public,return,strictfp,\
    short,static,super,switch,synchronized,this,throw,throws,transient,try,void,volatile,while"
    for java_file in java_files:
        if not os.path.isfile(java_file):
            continue
        error_flag = False
        content = ""
        with open(java_file, 'rb') as r:
            content = r.read()
            # 替换方法名
            for private_function_name in re.compile(rb"(?:public|private|protected) (?:static )?\w+ (\w+)\(").findall(content):
                if private_function_name in java_keys.split(b","):
                    ori_str = private_function_name + b"("
                    rep_str = private_function_name + str(random.randint(1000,9999)).encode() + b"("
                    content = content.replace(ori_str, rep_str)
                    error_flag = True
            # 替换属性名
            for private_attribute_name in re.compile(rb"(?:public|private|protected) (?:static )?(?:final )?\w+(?:\[\])* (\w+) = ").findall(content):
                if private_attribute_name in java_keys.split(b","):
                    rand_num = str(random.randint(1000,9999)).encode()
                    ori_str = b" " + private_attribute_name + b" = "
                    rep_str = b" " + private_attribute_name + rand_num + b" = "
                    content = content.replace(ori_str, rep_str)

                    if  b"this." + private_attribute_name in content:
                        content = re.compile(rb"this\." + private_attribute_name + rb"(\W)").sub(rb'this.' + private_attribute_name + rand_num + rb'\1', content)
                        error_flag = True

                    if not private_attribute_name in b"byte,int,long,short,float".split(b","):
                        if re.compile(rb"\W" + private_attribute_name + rb'(?:\.|\(|\[\w|;|\+|\-)').findall(content):
                            content = re.compile(rb"(\W)" + private_attribute_name + rb'(\.|\(|\[\w|;|\+|\-)').sub(rb'\1' + private_attribute_name + rand_num + rb'\2', content)
                            error_flag = True
                    else:
                        if re.compile(rb"\W" + private_attribute_name + rb'(?:\.|\(|;|\+|\-)').findall(content):
                            content = re.compile(rb"(\W)" + private_attribute_name + rb'(\.|\(|;|\+|\-)').sub(rb'\1' + private_attribute_name + rand_num + rb'\2', content)
                            error_flag = True

                    if re.compile(rb"\w+\." + private_attribute_name + rb"\W+").search(content):
                        content = re.compile(rb"(\w+\.)" + private_attribute_name + rb'(\W+)').sub(rb'\1' + private_attribute_name + rand_num + rb'\2', content)
                        error_flag = True
        
        if error_flag:
            with open(java_file, 'wb') as w:
                w.write(content)

# 部分代码在反编译之后会出现相同类名的情况
def clearDuplicateClass(java_files):
    for java_file in java_files:
        if not os.path.isfile(java_file):
            continue
        error_flag = False
        content = ""
        with open(java_file, 'rb') as r:
            content = r.read()
            while True:
                classes = []
                flag = False
                for child_class in re.compile(rb"((?: +)(?:public|private|protected) (?:static )?class (\w+) )").findall(content):
                    if child_class[0] not in classes:
                        classes.append(child_class[0])
                    else:
                        rand_num = str(random.randint(1000,9999)).encode()
                        new_child_class = child_class[0].replace(child_class[1], child_class[1] + rand_num)
                        content = content.replace(child_class[0], new_child_class, 1)
                        flag = True
                        error_flag = True
                        break

                if not flag:
                    break
        if error_flag:
            with open(java_file, 'wb') as w:
                w.write(content)

# 修复重复定义字段
def clearDuplicateDeclare(java_files):
    for java_file in java_files:
        if not os.path.isfile(java_file):
            continue
        error_flag = False
        content = ""
        with open(java_file, 'rb') as r:
            content = r.read()
            if re.compile(rb" (\w+) = \1;").search(content):
                error_flag = True
                content = re.compile(rb"(, (\w+) = \2;)").sub(rb' ;',content)
        if error_flag:
            with open(java_file, 'wb') as w:
                w.write(content)

# 修复final字段重复定义
def repairFinalField(java_files):
    for java_file in java_files:
        if not os.path.isfile(java_file):
            continue
        error_flag = False
        content = ""

        with open(java_file, 'rb') as r:
            content = r.read()
            for t in re.compile(rb"(?:private|public|protected) final \w+ (\w+) = ").findall(content):
                if b"this." + t + b" = " in content:
                    content = re.compile(rb"(private|public|protected) final (\w+) (\w+) = ").sub(rb"\1 \2 \3 = ",content)
                    error_flag = True

        if error_flag:
            with open(java_file, 'wb') as w:
                w.write(content)
            

# 修复编码问题导致的编译异常
def clearCodingError(target_dir):
    pass

def clearTLD(target_dir):
    # 老版本的代码中出现的tld引用在新版中不支持，需要去除tld引入
    # <%@ taglib uri="/WEB-INF/tags/convert.tld" prefix="f"%>
    for jsp_file in getFilesFromPath(target_dir, "jsp"):
        if not os.path.isfile(jsp_file):
            continue
        error_flag = False
        content = ""
        with open(jsp_file, 'rb') as r:
            content = r.read()
            for prefix in re.compile(rb'''<%@\s+taglib.*?uri=\".*?\.tld\".*?prefix=\"(.*?)\".*?%>''').findall(content):
                content = content.replace(prefix + b":", b"")

            if re.compile(rb'''<%@\s+taglib.*?uri=\".*?\.tld\".*?%>''').findall(content):
                content = re.compile(rb'''<%@\s+taglib.*?uri=\".*?\.tld\".*?%>''').sub(b"", content)
                error_flag = True

        if error_flag:
            with open(jsp_file, 'wb') as w:
                w.write(content)

        
def clearJava(target_files):
    clearPackage(target_files)
    clearDuplicateClass(target_files)
    clearDuplicateDeclare(target_files)
    repairNoneDeclare(target_files)
    repairKeyPrivateFunction(target_files)
    repairFinalField(target_files)


def clearSource(target_dir):
    clearTLD(target_dir)
    pass

