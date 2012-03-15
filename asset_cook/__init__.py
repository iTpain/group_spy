import os
import re
from hashlib import md5

def walk_directory_recursively(path, ext):
    for dirname, directories, file_names in os.walk(path, followlinks=True):
        for file in file_names:
            if file.split(".")[-1] == ext:
                yield (dirname + file, file)
                
def process_templates(templates_path, js_path, css_path):
    index = 0
    for template_file_name, short_name in walk_directory_recursively(templates_path, "html"):
        f = open(template_file_name, "r")
        file_content = f.read()
        template_copy = file_content.strip()
        f.close()
        prev_match = 0
        group_start = 0
        js_group = []
        for match in re.finditer(r'<script src="{{ STATIC_URL }}js/([/.A-Za-z_-]+\.js)"></script>', file_content):
            match_start = match.start()
            js_file = file_content[match.start(1) : match.end(1)]
            if js_file == "global.js":
                continue
            delimiters_count = file_content[prev_match : match_start].count("\n")
            if delimiters_count > 1 and prev_match > 0:
                index += 1
                global_js_file = compile_js_group(js_path, [js[0] for js in js_group], short_name, index)
                template_copy = template_copy.replace("global.js", global_js_file)
                js_group = []
            js_group.append((js_file, match_start))
            prev_match = match_start
        index += 1
        global_js_file = compile_js_group(js_path, [js[0] for js in js_group], short_name, index)
        if global_js_file:
            template_copy = template_copy.replace("global.js", global_js_file)
        f = open(template_file_name, "w")
        f.write(template_copy)
        f.close()
        
def compile_js_group(js_path, js_group, template, index):
    if not js_group:
        return
    free_js = []
    module_js = []
    discovered_set = {js for js in js_group}
    counter = 0
    while len(js_group) > counter:
        js = js_group[counter]
        js_file_handle = open(js_path + js, "r")
        js_file = js_file_handle.read()
        js_file_handle.close()
        match = re.match(r"new Module\('.+', \[(.*)\]", js_file)
        if match:
            dependencies = [piece.strip(" '\"") for piece in match.group(1).split(",") if len(piece) > 0]
            for p in dependencies:
                if not p in discovered_set:
                    discovered_set.add(p)
                    js_group.append(p)
            module_js.append([js, dependencies])
        else:
            free_js.append(js_file)
        counter += 1
    modules = {js[0]: {dep for dep in js[1]} for js in module_js}
    ordered_modules = []
    while len(modules.keys()) > 0:
        to_remove = []
        for module, deps in modules.iteritems():
            if len(deps) == 0:
                ordered_modules.append(module)
                for m, d in modules.iteritems():
                    if module in d:
                        d.remove(module)
                to_remove.append(module)
        for el in to_remove:
            del modules[el]
    for module in ordered_modules:
        handle = open(js_path + module, "r")
        module_content = handle.read()
        pieces = module_content.split("\n")[1:]
        while pieces[-1].strip(" \t") != "})":
            pieces.pop()
        pieces.pop()
        free_js.append("\n".join(pieces))
        handle.close()
    total_js = "\n\n".join(free_js)
    md5hasher = md5()
    md5hasher.update(total_js)
    hash = md5hasher.hexdigest()
    short_name = template + "-" + str(index) + "-" + hash + ".js"
    f = open(js_path + short_name, "w")
    f.write(total_js)
    f.close()
    return short_name